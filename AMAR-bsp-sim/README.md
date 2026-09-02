# Rover Bio-Scan Simulation

A small Python project that simulates the "bio-scan" system of a rover.
It takes a real recorded body signal and runs it through the four basic
steps of Biomedical Signal Processing (BSP): sampling, frequency analysis,
filtering and windowing.

Everything runs from one file (`rover_bsp_sim.py`) and saves four figures
plus a short text report inside `outputs/`.

---

## Where the data comes from

| | |
|---|---|
| Dataset name | `bio_resting_5min_100hz` |
| What it is | A real 5-minute resting-state recording of one person: ECG (heart), PPG (pulse at the finger) and RSP (breathing) |
| Sampling rate | 100 Hz (100 samples every second, so 30,000 samples in total) |
| Where it is from | Sample dataset bundled with the open-source **NeuroKit2** library, hosted in its public GitHub data folder (`neuropsychology/NeuroKit`) |
| How it is imported | `nk.data("bio_resting_5min_100hz")` inside `load_dataset()`. NeuroKit2 downloads it automatically the first time you run the script, so there is no manual download step |
| Which channel we use | The `ECG` column only |

This is real recorded data, not a sine wave that we generated ourselves.
That matters, because a synthetic signal would be perfectly clean and the
filtering and artifact steps would have nothing to do.

Want to use your own rover sensor file instead? Change only `load_dataset()`.
It just has to return `(time_array, signal_array)` and you have to set `FS`
to your sampling rate. You can also switch to `df["PPG"]` or `df["RSP"]` from
the same dataset if you want a non-heart channel.

---

## The four steps in simple words

### Step 1 - Sampling (`demo_aliasing`)
A sensor does not record continuously; it takes snapshots (samples) many
times per second. The Nyquist rule says you must sample at least twice as
fast as the fastest wiggle in the signal. If you sample too slowly, the
recorded wave looks like a completely different, slower wave. That mistake
is called **aliasing**.

In the code we take 3 seconds of the ECG and throw away 7 out of every 8
samples, which drops the rate from 100 Hz to 12.5 Hz. The plot shows the
good version on top and the broken version below.

**Figure:** `outputs/1_sampling.png`

### Step 2 - Frequency analysis (`freq_analysis`)
Looking at the signal against time tells you *when* things happen. Looking
at it against frequency tells you *what is repeating and how often*. We use
Welch's method, which chops the signal into pieces, runs an FFT on each
piece and averages the results, so the spectrum is smoother than a plain FFT.

The peak inside 0.7-2.0 Hz is the heartbeat rhythm (0.7-2.0 Hz is about
42-120 beats per minute, i.e. a normal resting range).

**Small but important detail:** at first the code searched a wider band and
kept picking a **harmonic** (2x or 3x the true rate) instead of the real
heart rate. That happens because a heartbeat spike is very sharp, and sharp
spikes put energy at multiples of their base frequency. Narrowing the search
to a realistic resting range fixed it. We also cross-check this number
against the heart rate found in Step 4 from the actual peaks in time - if the
two agree, the frequency analysis is trustworthy.

**Figure:** `outputs/2_frequency.png`

### Step 3 - Filtering (`filter_signal`)
A raw recording contains things we do not want:
* slow drift below 0.5 Hz (breathing, the sensor slipping on the skin)
* electrical noise above 40 Hz (mains hum, muscle activity)

So we apply a **Butterworth bandpass filter** that keeps only 0.5-40 Hz.
We apply it with `filtfilt`, which runs the filter forwards and then
backwards. Doing it both ways cancels the time delay a filter normally adds,
so the peaks stay exactly where they were. That is called zero-phase
filtering, and it matters when you later measure the time between beats.

**Figure:** `outputs/3_filtering.png`

### Step 4 - Windowing and bad-frame detection (`windowed_scan`)
A body signal is not constant - the heart rate changes over the 5 minutes.
So one number for the whole recording is useless. We cut the signal into
10-second **frames** and analyse each frame separately.

In each frame we find the R-peaks (the tall spikes of the heartbeat),
measure the gap between them and convert it into beats per minute:

```
heart rate (bpm) = 60 / average gap between peaks (seconds)
```

If a frame gives an impossible value (under 40 or over 180 bpm) or no peaks
are found, we mark that frame as an **artifact** - probably the rover moved
or the sensor lost contact - and leave it out of the average. On the plot
good frames are green dots and bad frames are red crosses.

**Figure:** `outputs/4_windowed_hr.png`

---

## How to run it

```bash
git clone <your-repo-url>
cd rover-bsp-sim

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python3 rover_bsp_sim.py
```

The first run needs internet, because NeuroKit2 fetches the dataset.
After that it is cached locally.

## What you get in `outputs/`

| File | What it shows |
|---|---|
| `1_sampling.png` | Correctly sampled vs. under-sampled wave |
| `2_frequency.png` | Power at each frequency, heart-rate band highlighted |
| `3_filtering.png` | Signal before and after the bandpass filter |
| `4_windowed_hr.png` | Heart rate per 10-second frame, bad frames in red |
| `scan_report.txt` | Text summary: sampling rate, main frequency, average heart rate, number of bad frames |

## Files in this repo

```
rover-bsp-sim/
├── rover_bsp_sim.py    # the whole pipeline
├── requirements.txt    # libraries needed
├── README.md           # this file
├── docs/
│   └── explanation.md  # longer notes, useful for the presentation
├── .gitignore
└── outputs/            # created automatically when you run the script
```

## Libraries used

* **numpy** - arrays and maths
* **scipy.signal** - Welch PSD, Butterworth filter, filtfilt
* **neurokit2** - the dataset and the R-peak detector
* **matplotlib** - the plots
