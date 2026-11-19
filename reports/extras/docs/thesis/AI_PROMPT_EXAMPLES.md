# Prompt examples and original messages

Prepared on 19 November 2026 for the thesis documentation.

The two examples below use simple wording like my messages in this chat.
They are reconstructed summaries of requests in the saved project records.
They are not the original implementation messages or a complete prompt log.
Original messages available in this conversation are copied separately below.

## 1. Implementation and experimentations

Reconstructed example based on the saved implementation request.

```text
can you check what is already there in the project first?
go through the code and the previous results before changing anything.
i want to compare the individual models and the fusion methods.
check the datasets and what the labels actually mean.
check if the video and sensor inputs belong to the same sample.
make sure samples from the same group dont end up on both sides of the split.
keep the experiment settings fixed before checking the test results.
use the same evaluation setup for the models being compared in each study.
check how the predictions for training the fusion model are generated.
keep the assessment samples separate from training and model selection.
run the planned experiments only if the required checks pass.
keep the existing results and save the new work separately.
save the configs, seeds, predictions and the training details.
if something fails, keep the failed attempt and explain what happened.
also check the planned missing or degraded modality conditions.
report when fusion helps, when it does not, and when the result is unclear.
dont change the experiment just to get a better score.
keep the folders clear so i can follow what was done later.
```

Source: [preserved implementation request][implementation].
This summarises part of that request; it does not establish task completion.

## 2. Fetching and checking the results

Reconstructed example based on the saved audit request and this conversation.

```text
can you fetch the saved results from the experiments?
i need the csv files, figures, matrices and the technical results for my thesis.
first check which files are actually available.
keep the results connected to the correct experiment and configuration.
check the sample ids and labels before comparing the predictions.
check the reported numbers from the saved predictions where possible.
keep results from different tasks and datasets clearly identified.
explain what the individual models and fusion methods actually did.
show the comparison tables and figures that support the conclusions.
include the failures and the results where there was no clear improvement.
mention if a result is incomplete or if the required file is missing.
explain the limitations in simple words so i can use them in the thesis.
also check what i would need to keep these results on my laptop.
check which files can go to github and what needs a separate download.
dont call the upload complete before checking the required files.
```

Sources: [preserved audit request][audit] and this conversation.
The GitHub discussion checked feasibility; it did not perform an upload.

## Original messages available in this conversation

The following are copied as typed, including spelling and punctuation.
They concern results access; they are not the older implementation prompts.

> how big it would be If I would like to have the reaults and csvÄs and stuff in my local laptop like uploaded to GIT and used locallz instead of requiring to use HFU Server and VPNS

> is that possible with Github`commits to upload them? so that all the results and figures and matrix and required technical results are available?#

## Source records

The earlier original implementation chats were not recovered from the available sources.
The linked files preserve task instructions; they do not establish who drafted every line.
Generated future prompts in the workflow starter kit are not counted as past messages.
Completed and unfinished work must be checked in the relevant experiment records.

[implementation]: ../../../../CROSS_DATASET_COMPARISON/provenance/task_authorization.txt
[audit]: ../../../../docs/thesis/FINAL_VALIDITY_AUDIT_EXECUTION_PROMPT.md
