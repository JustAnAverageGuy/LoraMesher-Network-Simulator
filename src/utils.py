import math

def calculate_snr_rssi(distance_km, tx_power_dbm = 20, frequency_mhz=868,
                                    bandwidth_hz=125000, noise_figure_db=6,
                                    d0_m=1.0, path_loss_exponent=2.7):
    """
    Calculate RSSI and SNR using the Log-Distance Path Loss Model.

    Parameters:
        distance_m (float): Distance between nodes (km)
        tx_power_dbm (float): Transmit power (dBm)
        frequency_mhz (float): Frequency in MHz (default: 868)
        bandwidth_hz (float): Bandwidth in Hz (default: 125 kHz)
        noise_figure_db (float): Receiver noise figure in dB (default: 6)
        d0_m (float): Reference distance in meters (default: 1 m)
        path_loss_exponent (float): Path loss exponent (2=free space, higher for urban/indoor)

    Returns:
        tuple: (RSSI in dBm, SNR in dB)
    """

    # Step 1: Path loss at reference distance (FSPL)
    distance_m = distance_km * 1000.0 
    pl_d0_db = 20 * math.log10(d0_m / 1000.0) + 20 * math.log10(frequency_mhz) + 32.44

    # Step 2: Log-distance model path loss
    path_loss_db = pl_d0_db + 10 * path_loss_exponent * math.log10(distance_m / d0_m)

    # Step 3: RSSI
    rssi_dbm = tx_power_dbm - path_loss_db

    # Step 4: Noise floor
    thermal_noise_dbm = -174 + 10 * math.log10(bandwidth_hz) + noise_figure_db

    # Step 5: SNR
    snr_db = rssi_dbm - thermal_noise_dbm

    return rssi_dbm, snr_db

def lora_max_range(
    tx_power_dbm,
    sf,
    frequency_mhz=868.0,
    bandwidth_hz=125_000,
    noise_figure_db=6.0,
    path_loss_exp=2.7,    # 2 (free space), ~2.3–3.2 (rural/suburban/urban)
    d0_m=1.0,
    fade_margin_db=10.0,  # link margin to keep in reserve
    g_tx_dbi=0.0,
    g_rx_dbi=0.0,
    misc_losses_db=0.0    # cables, mismatch, polarization, etc.
):
    """
    Returns (max_range_m, sensitivity_dbm, pl_max_db, pl_d0_db)
    """
    # 1) SNR_min by SF (approx for 125 kHz BW)
    snr_min_table = {7: -7.5, 8: -10.0, 9: -12.5, 10: -15.0, 11: -17.5, 12: -20.0}
    if sf not in snr_min_table:
        raise ValueError("sf must be one of 7..12")
    snr_min_db = snr_min_table[sf]

    # 2) Receiver sensitivity
    sensitivity_dbm = -174 + 10*math.log10(bandwidth_hz) + noise_figure_db + snr_min_db

    # 3) Max allowable path loss (subtract margin & other losses)
    pl_max_db = (tx_power_dbm + g_tx_dbi + g_rx_dbi
                 - misc_losses_db - fade_margin_db - sensitivity_dbm)

    # 4) Path loss at reference distance d0 (FSPL, km/MHz units)
    d0_km = d0_m / 1000.0
    pl_d0_db = 20*math.log10(d0_km) + 20*math.log10(frequency_mhz) + 32.44

    # 5) Invert log-distance model to get max distance
    exponent = (pl_max_db - pl_d0_db) / (10 * path_loss_exp)
    max_range_m = d0_m * (10 ** exponent)
    return max_range_m