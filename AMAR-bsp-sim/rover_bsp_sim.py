"""
Rover Bio-Scan Simulation (Biomedical Signal Processing)
========================================================
This script pretends to be the rover's on-board "bio-scan" system.
It takes a real recorded body signal (ECG - the electrical activity of a
heart) and pushes it through the four basic steps of signal processing:

  Step 1: Sampling and aliasing  -> why the sampling rate matters
  Step 2: Frequency analysis     -> see the signal as frequencies, not time
  Step 3: Filtering              -> remove noise, keep the useful part
  Step 4: Windowing              -> cut into small frames, find heart rate,
                                    mark bad frames

Dataset used: "bio_resting_5min_100hz" from the NeuroKit2 library.
It is a real 5-minute resting-state recording of one person (ECG, PPG and
breathing), sampled at 100 samples per second. NeuroKit2 downloads it
automatically from its public GitHub data folder the first time you run
this file, so no manual download is needed.

Run:
    python3 rover_bsp_sim.py

It creates:
    outputs/*.png            -> one picture per step
    outputs/scan_report.txt  -> short text summary of the scan
"""

import os

import matplotlib

matplotlib.use("Agg")  # save figures to files instead of opening windows
import matplotlib.pyplot as plt
import neurokit2 as nk
import numpy as np
from scipy import signal as sig

OUT = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT, exist_ok=True)

FS = 100        # sampling rate of the dataset (100 samples per second)
WINDOW_SEC = 10  # size of one scan frame, in seconds


# ---------------------------------------------------------------------------
# Load the dataset
# ---------------------------------------------------------------------------
def load_dataset():
    """Load the real ECG recording that the rover will 'scan'.

    Source: NeuroKit2 sample dataset "bio_resting_5min_100hz"
    (5 minutes, 100 Hz, real human resting-state recording).
    To use your own rover sensor CSV instead, only this function needs to
    change - it just has to return (time_array, signal_array).
    """
    df = nk.data("bio_resting_5min_100hz")
    ecg_raw = df["ECG"].values.astype(float)
    t = np.arange(len(ecg_raw)) / FS
    return t, ecg_raw


# ---------------------------------------------------------------------------
# Step 1: Sampling and aliasing
# ---------------------------------------------------------------------------
def demo_aliasing(t, ecg_raw):
    """Show what happens when we take too few samples per second.

    Nyquist rule: the sampling rate must be at least twice the highest
    frequency in the signal. If we break this rule, the shape of the wave
    gets distorted - this is called aliasing.
    """
    seg_sec = 3
    n = seg_sec * FS
    seg_t, seg = t[:n], ecg_raw[:n]

    # keep only every 8th sample -> effective rate of 12.5 Hz (too low)
    down_factor = 8
    down_t, down_seg = seg_t[::down_factor], seg[::down_factor]

    fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axs[0].plot(seg_t, seg, color="tab:blue", lw=1)
    axs[0].set_title(f"Enough samples ({FS} Hz) - shape looks correct")
    axs[0].set_ylabel("Amplitude")

    axs[1].plot(down_t, down_seg, "o-", color="tab:red", lw=1, ms=3)
    axs[1].set_title(
        f"Too few samples ({FS / down_factor:.1f} Hz) - shape gets distorted (aliasing)"
    )
    axs[1].set_ylabel("Amplitude")
    axs[1].set_xlabel("Time (s)")
    fig.suptitle("Step 1: Sampling rate matters")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "1_sampling.png"), dpi=140)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Step 2: Frequency analysis (time domain -> frequency domain)
# ---------------------------------------------------------------------------
def freq_analysis(ecg_raw):
    """Find which frequencies carry most of the power in the signal.

    Welch's method splits the signal into pieces, does an FFT on each and
    averages them, which gives a smoother and more reliable spectrum than
    a single FFT of the whole signal.
    """
    freqs, psd = sig.welch(ecg_raw, fs=FS, nperseg=1024)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.semilogy(freqs, psd, color="tab:purple")
    ax.set_xlim(0, 50)
    ax.set_xlabel("Frequency (Hz)")
    ax.set_ylabel("Power")
    ax.set_title("Step 2: Which frequencies are present in the signal")
    ax.axvspan(0.7, 2.0, color="green", alpha=0.15, label="Normal heart-rate band")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "2_frequency.png"), dpi=140)
    plt.close(fig)

    # A heartbeat spike is sharp, so it also has strong harmonics (2x, 3x the
    # real rate). If we search a wide band we may pick a harmonic by mistake.
    # So we search only 0.7-2.0 Hz, which is about 42-120 beats per minute.
    band_mask = (freqs > 0.7) & (freqs < 2.0)
    band_freqs, band_psd = freqs[band_mask], psd[band_mask]
    dominant_freq = band_freqs[np.argmax(band_psd)]
    return dominant_freq


# ---------------------------------------------------------------------------
# Step 3: Digital filtering
# ---------------------------------------------------------------------------
def filter_signal(ecg_raw):
    """Keep 0.5-40 Hz and throw away the rest.

    Below 0.5 Hz is mostly slow drift (breathing, electrode movement) and
    above 40 Hz is mostly electrical noise. filtfilt runs the filter forward
    and backward so the output is not shifted in time (zero phase).
    """
    low, high = 0.5, 40.0
    b, a = sig.butter(N=4, Wn=[low, high], btype="bandpass", fs=FS)
    ecg_filt = sig.filtfilt(b, a, ecg_raw)

    fig, ax = plt.subplots(figsize=(10, 4))
    seg = slice(0, FS * 6)  # show the first 6 seconds
    t_seg = np.arange(seg.stop) / FS
    ax.plot(t_seg, ecg_raw[seg], label="Before filtering", alpha=0.6)
    ax.plot(t_seg, ecg_filt[seg], label="After filtering (0.5-40 Hz)", lw=1.5)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Amplitude")
    ax.set_title("Step 3: Cleaning the signal with a filter")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "3_filtering.png"), dpi=140)
    plt.close(fig)
    return ecg_filt


# ---------------------------------------------------------------------------
# Step 4: Windowing and bad-frame detection
# ---------------------------------------------------------------------------
def windowed_scan(t, ecg_filt):
    """Cut the signal into 10-second frames and measure heart rate in each.

    A body signal changes over time, so one number for the whole recording
    is not enough. We find the R-peaks (the tall spikes) inside each frame,
    convert the gap between peaks into beats per minute, and mark a frame as
    bad if the value is impossible for a human (below 40 or above 180 bpm).
    """
    win_len = WINDOW_SEC * FS
    n_windows = len(ecg_filt) // win_len

    window_times, heart_rates, artifact_flags = [], [], []

    for i in range(n_windows):
        seg = ecg_filt[i * win_len:(i + 1) * win_len]
        window_times.append(i * WINDOW_SEC + WINDOW_SEC / 2)

        try:
            _, info = nk.ecg_peaks(seg, sampling_rate=FS)
            r_peaks = info["ECG_R_Peaks"]
            if len(r_peaks) >= 2:
                rr = np.diff(r_peaks) / FS       # seconds between beats
                hr = 60 / np.mean(rr)            # beats per minute
                artifact = not (40 <= hr <= 180)  # simple sanity check
            else:
                hr, artifact = np.nan, True
        except Exception:
            hr, artifact = np.nan, True

        heart_rates.append(hr)
        artifact_flags.append(artifact)

    window_times = np.array(window_times)
    heart_rates = np.array(heart_rates)
    artifact_flags = np.array(artifact_flags)

    fig, ax = plt.subplots(figsize=(10, 4))
    good = ~artifact_flags
    ax.plot(window_times[good], heart_rates[good], "o-", color="tab:green",
            label="Good frame")
    ax.plot(window_times[artifact_flags], heart_rates[artifact_flags], "x",
            color="tab:red", label="Bad frame", ms=10)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Heart rate (bpm)")
    ax.set_title(f"Step 4: Heart rate in every {WINDOW_SEC} second frame")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "4_windowed_hr.png"), dpi=140)
    plt.close(fig)

    return window_times, heart_rates, artifact_flags


# ---------------------------------------------------------------------------
# Final text report
# ---------------------------------------------------------------------------
def write_report(dominant_freq, window_times, heart_rates, artifact_flags):
    valid_hr = heart_rates[~artifact_flags]
    lines = [
        "ROVER BIO-SCAN REPORT",
        "=" * 40,
        "Dataset: NeuroKit2 'bio_resting_5min_100hz' (real ECG recording)",
        f"Sampling rate: {FS} Hz",
        f"Scan length: {window_times[-1] + WINDOW_SEC / 2:.0f} s "
        f"({len(window_times)} frames of {WINDOW_SEC}s each)",
        "",
        f"Main frequency found: {dominant_freq:.2f} Hz "
        f"(about {dominant_freq * 60:.0f} bpm)",
        "",
        f"Frames checked: {len(window_times)}",
        f"Bad frames: {int(artifact_flags.sum())}",
        f"Average heart rate (good frames): {np.nanmean(valid_hr):.1f} bpm"
        if len(valid_hr) else "Average heart rate: not available",
        f"Heart rate range: {np.nanmin(valid_hr):.1f}-{np.nanmax(valid_hr):.1f} bpm"
        if len(valid_hr) else "",
        "",
        "Figures created:",
        "  Step 1 sampling      -> 1_sampling.png",
        "  Step 2 frequency     -> 2_frequency.png",
        "  Step 3 filtering     -> 3_filtering.png",
        "  Step 4 windowing     -> 4_windowed_hr.png",
    ]
    report_text = "\n".join(lines)
    with open(os.path.join(OUT, "scan_report.txt"), "w") as f:
        f.write(report_text)
    print(report_text)


# ---------------------------------------------------------------------------
def main():
    t, ecg_raw = load_dataset()
    demo_aliasing(t, ecg_raw)
    dominant_freq = freq_analysis(ecg_raw)
    ecg_filt = filter_signal(ecg_raw)
    window_times, heart_rates, artifact_flags = windowed_scan(t, ecg_filt)
    write_report(dominant_freq, window_times, heart_rates, artifact_flags)


if __name__ == "__main__":
    main()
