import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from matplotlib.gridspec import GridSpec

# ============================================================
# Coupled Oscillator Network for Fusion Engine
# Core - Vapor - Plasma - Shell
# ============================================================

def coupled_oscillators(t, y, params):
    """
    y = [theta_c, dtheta_c, theta_p, dtheta_p, theta_v, dtheta_v, theta_s, dtheta_s]
    params = [w_c, w_p, w_v, w_s, gamma, k_cp, k_cs, k_pc, k_ps, k_pv, k_vp, k_vc, k_sc, k_sp]
    """
    theta_c, dtheta_c, theta_p, dtheta_p, theta_v, dtheta_v, theta_s, dtheta_s = y
    
    w_c, w_p, w_v, w_s, gamma, k_cp, k_cs, k_pc, k_ps, k_pv, k_vp, k_vc, k_sc, k_sp = params
    
    # Accelerations
    ddtheta_c = -gamma * dtheta_c - w_c**2 * theta_c + k_cp*(theta_p - theta_c) + k_cs*(theta_s - theta_c)
    ddtheta_p = -gamma * dtheta_p - w_p**2 * theta_p + k_pc*(theta_c - theta_p) + k_ps*(theta_s - theta_p) + k_pv*(theta_v - theta_p)
    ddtheta_v = -gamma * dtheta_v - w_v**2 * theta_v + k_vp*(theta_p - theta_v) + k_vc*(theta_c - theta_v)
    ddtheta_s = -gamma * dtheta_s - w_s**2 * theta_s + k_sc*(theta_c - theta_s) + k_sp*(theta_p - theta_s)
    
    return [dtheta_c, ddtheta_c, dtheta_p, ddtheta_p, dtheta_v, ddtheta_v, dtheta_s, ddtheta_s]

def run_simulation(w_c, w_p, w_v, w_s, gamma, coupling, t_max=200, dt=0.01):
    """Run simulation and return time series and frequencies"""
    
    # Coupling strengths (symmetric for now)
    k = coupling
    params = [w_c, w_p, w_v, w_s, gamma, k, k, k, k, k, k, k, k, k]
    
    t_span = (0, t_max)
    t_eval = np.arange(0, t_max, dt)
    y0 = [0.1, 0, 0.2, 0, 0.15, 0, 0.05, 0]  # small initial phases
    
    sol = solve_ivp(coupled_oscillators, t_span, y0, t_eval=t_eval, args=(params,), method='RK45', rtol=1e-6)
    
    t = sol.t
    theta_c = sol.y[0]
    theta_p = sol.y[2]
    theta_v = sol.y[4]
    theta_s = sol.y[6]
    
    # Compute frequencies after transients
    trans_idx = int(len(t) * 0.7)
    
    def get_freq(theta):
        # Simple zero-crossing frequency estimate
        crossings = np.where(np.diff(np.sign(theta[trans_idx:])))[0]
        if len(crossings) < 2:
            return 0
        periods = np.diff(crossings) * dt
        return 2 * np.pi / np.mean(periods)
    
    f_c = get_freq(theta_c)
    f_p = get_freq(theta_p)
    f_v = get_freq(theta_v)
    f_s = get_freq(theta_s)
    
    return t, theta_c, theta_p, theta_v, theta_s, f_c, f_p, f_v, f_s

# ============================================================
# Parameter Sweep: Lock-in Map
# ============================================================

def sweep_lock_in(w_c=1.0, w_s_range=(0.5, 3.0), w_p_range=(0.2, 3.0), 
                  coupling=0.4, gamma=0.2, n_points=40):
    """Sweep Δω and ω_p, measure lock-in strength"""
    
    delta_ws = np.linspace(w_s_range[0] - w_c, w_s_range[1] - w_c, n_points)
    w_ps = np.linspace(w_p_range[0], w_p_range[1], n_points)
    
    lock_strength = np.zeros((len(w_ps), len(delta_ws)))
    lock_ratios = np.zeros((len(w_ps), len(delta_ws), 2))  # f_p/f_c, f_s/f_c
    
    for i, w_p in enumerate(w_ps):
        for j, dw in enumerate(delta_ws):
            w_s = w_c + dw
            _, _, _, _, _, f_c, f_p, f_v, f_s = run_simulation(w_c, w_p, 0.5*w_p, w_s, gamma, coupling, t_max=150)
            
            if f_c > 0 and f_p > 0:
                ratio = f_p / f_c
                # Lock strength: how close to rational (1:1, 2:1, 3:2, golden)
                targets = [1.0, 2.0, 0.5, 1.5, 1.618]
                min_diff = min(abs(ratio - t) for t in targets)
                lock_strength[i, j] = np.exp(-min_diff / 0.1)  # Gaussian falloff
                lock_ratios[i, j, 0] = f_p / f_c
                lock_ratios[i, j, 1] = f_s / f_c
    
    return delta_ws, w_ps, lock_strength, lock_ratios

# ============================================================
# Run the sweep
# ============================================================

print("Running parameter sweep...")
delta_ws, w_ps, lock_strength, lock_ratios = sweep_lock_in(coupling=0.4, gamma=0.2, n_points=50)
print("Done.")

# ============================================================
# Visualization
# ============================================================

fig = plt.figure(figsize=(14, 10))
gs = GridSpec(2, 2, height_ratios=[1, 1])

# Plot 1: Lock-in Map (Δω vs ω_p)
ax1 = fig.add_subplot(gs[0, 0])
im1 = ax1.imshow(lock_strength.T, origin='lower', 
                 extent=[w_ps[0], w_ps[-1], delta_ws[0], delta_ws[-1]],
                 aspect='auto', cmap='hot')
ax1.set_xlabel('Plasma Frequency ω_p')
ax1.set_ylabel('Beat Frequency Δω = ω_s - ω_c')
ax1.set_title('Lock-in Strength (Warmer = Stronger Lock)')
plt.colorbar(im1, ax=ax1)

# Plot 2: Golden Ratio Slice (Δω/ω_p = 1.618)
ax2 = fig.add_subplot(gs[0, 1])
# Find slice where Δω/ω_p ≈ 1.618
X, Y = np.meshgrid(delta_ws, w_ps)
ratio_grid = X / Y
mask = np.abs(ratio_grid - 1.618) < 0.1
if np.any(mask):
    slice_strength = lock_strength.copy()
    slice_strength[~mask] = np.nan
    im2 = ax2.imshow(slice_strength.T, origin='lower',
                     extent=[w_ps[0], w_ps[-1], delta_ws[0], delta_ws[-1]],
                     aspect='auto', cmap='plasma')
    ax2.set_xlabel('Plasma Frequency ω_p')
    ax2.set_ylabel('Beat Frequency Δω')
    ax2.set_title('Golden Ratio Slice (Δω/ω_p = φ)')
    plt.colorbar(im2, ax=ax2)
else:
    ax2.text(0.5, 0.5, 'No golden ratio points in sweep', ha='center', va='center')
    ax2.set_title('Golden Ratio Slice')

# Plot 3: Time evolution at resonance
ax3 = fig.add_subplot(gs[1, :])
# Pick a resonant point
w_c = 1.0
w_p = 1.0
w_s = 2.0  # Δω = 1.0
w_v = 0.5
t, theta_c, theta_p, theta_v, theta_s, _, _, _, _ = run_simulation(w_c, w_p, w_v, w_s, gamma=0.2, coupling=0.4, t_max=100)

ax3.plot(t, theta_c, label='Core (ω_c)', linewidth=1.5)
ax3.plot(t, theta_p, label='Plasma (ω_p)', linewidth=1.5, alpha=0.8)
ax3.plot(t, theta_v, label='Vapor', linewidth=1.5, alpha=0.7)
ax3.plot(t, theta_s, label='Shell (ω_s)', linewidth=1.5, alpha=0.8)
ax3.set_xlabel('Time')
ax3.set_ylabel('Phase')
ax3.set_title('Time Evolution at Resonance (Δω = ω_p = 1.0)')
ax3.legend(loc='upper right')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# ============================================================
# Print lock-in summary
# ============================================================

print("\n" + "="*60)
print("LOCK-IN ANALYSIS SUMMARY")
print("="*60)

# Find strongest lock
max_idx = np.unravel_index(np.argmax(lock_strength), lock_strength.shape)
best_dw = delta_ws[max_idx[1]]
best_wp = w_ps[max_idx[0]]
print(f"\nStrongest lock: Δω = {best_dw:.2f}, ω_p = {best_wp:.2f}")
print(f"Ratio Δω/ω_p = {best_dw/best_wp:.3f}")

# Check golden ratio
ratio_grid = np.abs(delta_ws[:, np.newaxis] / w_ps - 1.618)
golden_idx = np.unravel_index(np.argmin(ratio_grid), ratio_grid.shape)
if ratio_grid[golden_idx] < 0.1:
    print(f"\nGolden ratio found at Δω = {delta_ws[golden_idx[0]]:.2f}, ω_p = {w_ps[golden_idx[1]]:.2f}")
    print(f"Lock strength there: {lock_strength[golden_idx[0], golden_idx[1]]:.3f}")

# Lock-in range width
lock_thresh = 0.5
lock_region = lock_strength > lock_thresh
if np.any(lock_region):
    dw_range = delta_ws[np.any(lock_region, axis=0)]
    wp_range = w_ps[np.any(lock_region, axis=1)]
    print(f"\nLock-in region (strength > {lock_thresh}):")
    print(f"  Δω range: {dw_range[0]:.2f} to {dw_range[-1]:.2f}")
    print(f"  ω_p range: {wp_range[0]:.2f} to {wp_range[-1]:.2f}")

print("\n" + "="*60)