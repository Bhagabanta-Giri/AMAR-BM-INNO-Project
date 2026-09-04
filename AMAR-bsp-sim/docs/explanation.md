# Detailed notes (for the presentation / viva)

These are the longer explanations behind the four steps. The README has the
short version; this file has the "why" you can use while presenting.

---

## 1. The dataset

**Name:** `bio_resting_5min_100hz`
**Source:** sample data of the open-source Python library **NeuroKit2**
(project `neuropsychology/NeuroKit` on GitHub). The library exposes it
through the function `nk.data("bio_resting_5min_100hz")`, which downloads the
CSV from the project's public data folder and returns it as a pandas
DataFrame.

**Contents:** one person, resting (sitting quietly, not exercising), recorded
for 5 minutes at 100 Hz. Columns:

| Column | Meaning |
|---|---|
| `ECG` | Electrocardiogram - the electrical activity of the heart |
| `PPG` | Photoplethysmogram - blood volume change measured with light |
| `RSP` | Respiration - the chest expanding and contracting |

We use `ECG`. 5 minutes x 60 s x 100 samples/s = 30,000 samples.

**Why a real dataset and not a generated sine wave:** a synthetic signal has
no drift, no muscle noise and no movement artifacts, so Step 3 (filtering)
and Step 4 (artifact flagging) would have nothing real to do. Using a real
recording means the results actually prove the pipeline works.

**How it maps onto the rover story:** the rover's bio-scanner would produce a
stream of sensor samples at a fixed rate. This dataset stands in for that
stream. Swapping in real rover telemetry means changing only `load_dataset()`.

---

## 2. Step-by-step theory

### Step 1 - Sampling and aliasing
* A continuous signal becomes digital by taking samples at a fixed rate `fs`.
* **Nyquist-Shannon theorem:** to reconstruct the signal correctly, `fs` must
  be more than twice the highest frequency present.
* If `fs` is too low, high frequencies "fold back" and appear as fake low
  frequencies. This is aliasing, and it cannot be undone afterwards.
* Practical fix in hardware: an analog low-pass (anti-aliasing) filter before
  the ADC.
* In the demo we keep every 8th sample, so 100 Hz becomes 12.5 Hz. The QRS
  spike of the heartbeat has content well above 6.25 Hz, so it gets mangled.

### Step 2 - Time domain to frequency domain
* The **FFT** converts a signal from amplitude-vs-time into amplitude-vs-
  frequency. It answers "which repeating rhythms make up this signal".
* A single FFT of a long noisy signal is very jagged. **Welch's method**
  splits the signal into overlapping segments (here `nperseg=1024`), takes
  the FFT of each, and averages the power. Result: a smooth, readable
  **Power Spectral Density (PSD)**.
* Reading the plot: the bump near 1-1.3 Hz is the heartbeat (about 60-80
  bpm). Very low frequencies are breathing and drift. Broad high-frequency
  content is noise plus the sharp edges of the QRS complex.
* **The harmonic trap:** a sharp spike is not a pure sine, so a heart beating
  at 1.1 Hz also produces peaks at 2.2 Hz, 3.3 Hz and so on. If you search a
  wide band for "the biggest peak", you can land on a harmonic and report
  double the real heart rate. We restrict the search to 0.7-2.0 Hz.
* **Validation:** compare the frequency-domain answer with the time-domain
  answer from Step 4 (counting actual R-peaks). If the two match, the
  spectrum was read correctly. This is a good answer to "how did you check
  your result".

### Step 3 - Digital filtering
* **Bandpass 0.5-40 Hz**, the standard diagnostic band for ECG.
  * Below 0.5 Hz: baseline wander from breathing and electrode movement.
  * Above 40 Hz: mains interference and muscle (EMG) noise.
* **Butterworth, order 4:** Butterworth is chosen because it has the flattest
  possible response in the passband (no ripple), so the shape of the
  heartbeat is not distorted. Higher order = sharper cut-off but more
  ringing; 4 is a common compromise.
* **IIR vs FIR:** Butterworth is IIR - it uses feedback, so it needs fewer
  coefficients than an FIR filter for the same sharpness, but it has a
  non-linear phase response.
* **`filtfilt` (zero-phase):** because IIR phase is non-linear, different
  frequencies would be delayed by different amounts and the peaks would
  shift. `filtfilt` filters forwards and then backwards, so the delays cancel
  exactly. Timing is preserved, which is essential before measuring the gaps
  between beats. Note that this doubles the effective filter order.

### Step 4 - Windowing and artifacts
* Body signals are **non-stationary**: their statistics change with time. So
  we analyse short frames where the signal can be treated as roughly steady.
* Frame length is a trade-off: short frames follow changes quickly but hold
  too few beats to be reliable; long frames are stable but smear out real
  changes. 10 s holds roughly 10-15 beats, which is a reasonable middle.
* Inside each frame `nk.ecg_peaks()` locates the R-peaks. The gaps between
  consecutive R-peaks are the **RR intervals**; `60 / mean(RR)` gives beats
  per minute.
* **Artifact rule:** a frame is flagged if the computed rate falls outside
  40-180 bpm, or if fewer than two peaks are found, or if peak detection
  throws an error. Flagged frames are excluded from the average instead of
  being silently trusted.
* On a real rover this is what stops a shaken sensor or a lost contact from
  corrupting the reported scan result.

---

## 3. Things you can say if asked "what would you improve"

* Use the RR intervals to compute **heart rate variability** (SDNN, RMSSD),
  which says more about physiological state than the average rate.
* Add a **notch filter** at 50/60 Hz for mains interference (our 40 Hz
  low-pass already removes it here, but a notch is the targeted tool).
* Replace the fixed 40-180 bpm rule with a statistical check on the RR
  intervals, so a frame is flagged when beats are inconsistent, not just when
  the average looks odd.
* Overlap the windows (e.g. 10 s frames every 5 s) for a smoother heart-rate
  curve.
* Run the same pipeline on the `PPG` and `RSP` channels to show it is not
  specific to ECG.
