PHM 2026 - BASIC EDA INTERPRETATION GUIDE
=========================================

1. HIGH-FREQUENCY DATA
Raw vibration is sampled extremely often.
It describes the fast mechanical motion of the gearbox.

In this dataset:
- Accel 1 = axial vibration
- Accel 2 = radial vibration

At this stage we only ask:
- What does the waveform look like?
- Is it centered around zero?
- How large is the vibration?
- Are there spikes?
- Are the two accelerometers different?


2. FREQUENCY DOMAIN
A vibration waveform is measured in time.
The FFT shows which repeating frequencies are present.

At beginner-EDA level we only inspect:
- where strong peaks exist
- whether axial/radial spectra look different
- whether later runs eventually show different frequency structure

Do not call a peak a fault before doing physics-aware analysis.


3. CONTEXT VARIABLES
PAU Speed, PAU Torque and Temperature describe HOW the machine was operated.

They are critical because:
a vibration increase can come from higher speed or higher load,
not necessarily from gear damage.


4. CONDITION INDICATORS
FM4, NA4, M6A and ALR are already-computed gear condition metrics.

Beginner EDA asks:
- what range do they have?
- are they stable or noisy?
- do they vary through time?

Advanced EDA later asks whether they separate Run-1, Run-3 and Run-5.


5. LOW-FREQUENCY DATA
Low-frequency data stores slowly changing / derived information at a much
lower data rate than raw vibration.

It is dramatically smaller and is useful for:
- machine operating condition
- condition indicators
- long-duration degradation trends


6. PHOTOS
The images show the physical gear teeth.

They provide a different modality from the sensor data:
sensor data = indirect machine response
photos      = direct visual evidence of tooth surface condition

The advanced project later connects these two.


7. IMPORTANT
Run-1, Run-3 and Run-5 should initially be described as:
- early lifecycle
- intermediate lifecycle
- late lifecycle

Do not automatically call them:
healthy / damaged / failed.