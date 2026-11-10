"""CPU tensor/ZIP inspection only. No model construction, forward or optimizer step."""
import audit as a
from pathlib import Path
import gc,json,pickletools,zipfile
import torch
from safetensors import safe_open

def main():
    torch.set_num_threads(2)
    config=a.read('00_experiments/visual_backbone_one_day/run_01_two_epoch_finetuning/config/resolved_config.json')
    folder=a.path(config['weights_dir']);original=a.used(folder/'model.safetensors','pinned pretrained tensor identities')
    original_state={}
    with safe_open(str(original),framework='pt',device='cpu') as f:
        prefix='model.backbone.model.'
        original_state={k[len(prefix):]:f.get_tensor(k) for k in f.keys() if k.startswith(prefix)}
    assert original_state
    processor=a.read(folder/'preprocessor_config.json')
    a.write('support/ACTUAL_PREPROCESSOR.json',processor)
    a.write('support/PINNED_PRETRAINED_IDENTITY.json',{'model':'PekingU/rtdetr_r18vd','revision':config['checkpoint_revision'],
        'files':[dict(a.INPUTS[a.rel(a.used(folder/n))]) for n in ['model.safetensors','config.json','preprocessor_config.json']],
        'CNN_state_keys':len(original_state),'object_detector_keys_executed':False})
    inventory=a.rows(a.OUT/'11_CHECKPOINT_INVENTORY.csv');details=[];changes=[];optimizer=[]
    chosen=[]
    for r in inventory:
        p=a.path(r['path'])
        if r['kind']=='LAST RECOVERY':
            with zipfile.ZipFile(a.used(p)) as z:
                name=next(n for n in z.namelist() if n.endswith('/data.pkl'));ops=list(pickletools.genops(z.read(name)))
            ss={v for op,v,_ in ops if op.name in ['BINUNICODE','SHORT_BINUNICODE','UNICODE']}
            assert {'optimizer','scheduler','random'}<=ss
            optimizer.append({'path':r['path'],'optimizer_state':True,'scheduler_state':True,'RNG_state':True,
                'parameter_group_names_in_pickle':sorted(ss&{'classifier','full_executed_CNN'}),
                'inspection':'static pickle opcodes only; no deserialization of recovery RNG objects'})
        elif r['kind']=='SELECTED BEST':chosen.append(r)
        elif r['model'] in ['fine_tuned_16_frames','fine_tuned_32_frames','finetuned32_two_epochs','frozen32_two_epochs']:
            if not any(x['model']==r['model'] for x in chosen):chosen.append(r)
    # Original frozen outer-refit heads are trained states, separate from the CNN archive.
    for p in sorted(a.path('runs/reassemble/20260927T154732Z-section1/checkpoints').glob('rtdetr_fold*.pt')):
        chosen.append({'path':a.rel(p),'model':'ORIGINAL_FROZEN_HEAD','kind':'ORIGINAL OUTER HEAD','run_id':a.rel(p)})
    # Temporal final-stage adaptation is a different architecture, not the mean-head study.
    cfg=a.read(a.OLD/'03_hyperparameter_configuration/EFFECTIVE_CONFIGURATIONS.json')
    for r in cfg:
        if r['dataset']=='REASSEMBLE' and r['model']=='V-FT_final_stage_temporal':chosen.append({'path':r['checkpoint_path'],'model':r['model'],'kind':'TEMPORAL FINAL-STAGE','run_id':r['run_id']})
    extra=[]
    for r in chosen:
        p=a.used(r['path'],'CPU weights-only tensor inspection');obj=torch.load(p,map_location='cpu',weights_only=True)
        state=obj.get('model',obj.get('state_dict',obj))
        assert isinstance(state,dict)
        tensors={k:v for k,v in state.items() if torch.is_tensor(v)}
        nested={k:list(v) for k,v in state.items() if isinstance(v,dict)}
        finite=all(bool(torch.isfinite(v).all()) for v in tensors.values())
        assert finite
        changed_by_stage={};same_by_stage={};running_changed=[]
        if 'stage' in state and isinstance(state['stage'],dict):
            candidates={'encoder.stages.3.'+k:v for k,v in state['stage'].items()}
        else:candidates={k[len('backbone.'):]:v for k,v in tensors.items() if k.startswith('backbone.')}
        for k,v in candidates.items():
            assert k in original_state and tuple(v.shape)==tuple(original_state[k].shape),(r['path'],k)
            group='embedder' if k.startswith('embedder.') else '.'.join(k.split('.')[:3])
            changed=not torch.equal(v,original_state[k]);target=changed_by_stage if changed else same_by_stage
            target[group]=target.get(group,0)+1
            if ('running_mean' in k or 'running_var' in k) and changed:running_changed.append(k)
        assert not running_changed
        if r['model']=='C_full_finetuned16':assert all(changed_by_stage.get(k,0)>0 for k in ['embedder','encoder.stages.0','encoder.stages.1','encoder.stages.2','encoder.stages.3'])
        if r['model'] in ['fine_tuned_16_frames','fine_tuned_32_frames','finetuned32_two_epochs','V-FT_final_stage_temporal']:
            assert changed_by_stage.get('encoder.stages.3',0)>0
            assert not any(k!='encoder.stages.3' for k in changed_by_stage)
        selected=obj.get('selected_epoch',obj.get('epoch',obj.get('epochs',a.U)))
        details.append({'path':a.rel(p),'sha256':a.sha(p),'model':r['model'],'kind':r['kind'],'payload_keys':list(obj),
            'state_keys':list(tensors),'nested_state_keys':nested,'tensor_count':len(tensors),'top_level_state_elements':sum(v.numel() for v in tensors.values()),
            'all_top_level_tensors_finite':finite,'selected_or_saved_epoch_in_payload':selected,
            'CPU_weights_only_load':'PASS','new_inference':'NOT EXECUTED','strict_module_reload':'NOT EXECUTED; source shapes and historical replay only',
            'changed_backbone_tensor_counts_by_stage':changed_by_stage,'unchanged_tensor_counts_by_stage':same_by_stage,'running_statistics_changed':running_changed})
        changes.append({'path':a.rel(p),'model':r['model'],'changed_CNN_stages':changed_by_stage,'running_statistics_unchanged':not running_changed,'original_pretrained_sha256':a.sha(original)})
        if not any(x['path']==a.rel(p) for x in inventory):extra.append({'run_id':r['run_id'],'model':r['model'],'path':a.rel(p),'kind':r['kind'],'bytes':p.stat().st_size,'sha256':a.sha(p),'selected_epoch':selected,'last_epoch':obj.get('epochs',a.U),'model_state_available':True,'optimizer_scheduler_RNG':'UNKNOWN / compact inference payload','verification':a.V})
        del obj,state,tensors,candidates;gc.collect()
    a.table('11_CHECKPOINT_INVENTORY.csv',inventory+extra)
    a.write('support/CHECKPOINT_CPU_TENSOR_INSPECTION.json',details)
    a.table('support/CHECKPOINT_ACTUAL_STAGE_CHANGES.csv',changes)
    a.table('support/RECOVERY_OPTIMIZER_SCHEDULER_RNG.csv',optimizer)
    a.table('support/CHECKPOINT_INSPECTION_INPUTS.csv',list(a.INPUTS.values()))
    print(json.dumps({'CPU_selected_tensor_payloads':len(details),'recovery_states_statically_verified':len(optimizer),'new_neural_forwards':0}))

if __name__=='__main__':main()
