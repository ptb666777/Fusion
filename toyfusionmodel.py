import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

# Constants / Base Parameters (tunable)
R_base = 1.2          # base radius (m)
scale_factors = np.array([1, 2, 4, 5, 10, 100, 1000])
torque_base = 1e6     # base torque from particle hits (Nm) - tuned for realism
drag_coeff = 1e-6     # quadratic drag coefficient
field_inner = 100     # T (dipole)
field_outer = 100     # T (quad)
angle_deg = 35        # outer surface angle (shallower = more bounce)
twist_deg = 25        # helical rifling twist
viscosity_factor = 2  # thicker outer shell (higher = more torque capture)

def torque_from_particles(scale, angle, twist, viscosity):
    """Net torque from angled/rifled hits + viscosity bonus"""
    efficiency = np.sin(np.deg2rad(angle)) * (1 + twist/90)  # 0-1
    return torque_base * (scale**3) * efficiency * viscosity  # volume scaling

def drag(omega):
    return -drag_coeff * omega**2

def domega_dt(omega, t, scale, angle, twist, visc):
    tau = torque_from_particles(scale, angle, twist, visc)
    d = drag(omega)
    return (tau + d) / (1 + scale)  # inertia scales with size

# Time array for integration
t = np.linspace(0, 10, 1000)  # 10 seconds sim

# Run for each scale
results = {}
for s in scale_factors:
    omega0 = 200  # initial rad/s
    sol = odeint(domega_dt, omega0, t, args=(s, angle_deg, twist_deg, viscosity_factor))
    omega = sol[:, 0]
    
    # Proxy metrics
    power_proxy = (s**3) * 1          # ~R^3 fusion power
    confinement = np.clip(0.5 + 0.1 * np.log(s + 1), 0, 1)  # improves with size
    tau_proxy = 20 * np.sqrt(s)       # confinement time
    
    results[s] = {
        'time': t,
        'omega': omega,
        'final_omega': omega[-1],
        'power_GW_proxy': power_proxy,
        'confinement': confinement,
        'tau_s': tau_proxy
    }

# Plot spin evolution for a few scales
plt.figure(figsize=(10, 6))
for s in [1, 4, 10, 100]:
    plt.plot(results[s]['time'], results[s]['omega'], label=f'{s}x scale')
plt.xlabel('Time (s)')
plt.ylabel('Angular Velocity (rad/s)')
plt.title('Spin-up & Stabilization vs Scale')
plt.legend()
plt.grid(True)
plt.show()

# Print summary table
print("Scale | Final Spin (rad/s) | Power Proxy (GW) | Confinement (0-1) | Tau (s)")
for s in scale_factors:
    r = results[s]
    print(f"{s:4d}  | {r['final_omega']:14.0f}      | {r['power_GW_proxy']:16.0f} | {r['confinement']:17.2f} | {r['tau_s']:7.1f}")