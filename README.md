# diseqc-audio

Simple python script to send commands to a DiSEqC Motor via audio output. This was designed to control a Sattelite Positioner with a Raspberry Pi.

## DiSEqC Protocol

"The DiSEqC system is a communication bus between satellite receivers and
satellite peripheral equipment".
It works by sending both the $12\pm1V$ DC, to power the motor and all the electronics, as well as a $`22 kHz (\pm 20 \% )`$ control signal, which should be $650 \pm 250 mV$ peak-peak, on the same coaxial cable. Firstly, we need to understand how to construct the actual message that needs to be delivered.

### Data-Bit Signalling

Starting from the smallest element of digital information, data-bit signalling "uses base-band timings of $(500\pm100)\mu s$ for a one-third bit PWK (Pulse Width Keying) coded signal period on a nominal $`22 kHz (\pm 20\%)`$ carrier". This means that:

- Bit 0 - $(1.0\pm0.2)ms$ tone, nominally 22 cycles, followed by $(0.5\pm0.1)ms$ of silence

- Bit 1 - $(0.5\pm0.1)ms$ tone, nominally 11 cycles, followed by $(1.0\pm0.2)ms$ of silence

![DiSEqC Modulation Scheme](./images/diseqc_modulation.png)

### Message Data Format

DiSEqC messages consist of one or more bytes, with each bit as defined
in the previous section, and each byte followed by an odd parity bit .
The commands from the master are structured as follows:

<div id="tab:command">

| Framing | P   | Address | P   | Command | P   | Data | P   |
| :------ | :-- | :------ | :-- | :------ | :-- | :--- | :-- |

Basic DiSEqC command structure

</div>

To move the positioner to a given angle, the command we want to send is:

<div id="tab:diseqcmove">

| E1  | P   | 31  | P   | 6E  | P   | E/D XX.X | P   |
| :-- | :-- | :-- | :-- | :-- | :-- | :------- | :-- |

Command move to position (hex)XX.X

</div>

Looking at what each of those blocks represent:

- _P_ - Odd Parity Bit;

- _E1_ - Framing signalling Command from Master, No reply required,
  Repeated transmission;

- _31_ - Address of Polar/Azimuth Positioner;

- _6E_ - Command Drive Motor to Angular Position;

- _E/D XX.X_ - _E_ denotes "east of 0" and _D_ "west of 0", while
  _XX.X_ is the target angle, in hexadecimal.

In order to generate the control signal, the Raspberry Pi’s built-in
audio driver and 3.5mm jack output were used. This might seem like an
unconventional decision, but it is actually a solid solution. Audio
drivers are generally rated to generate signals with a frequency range
of 20-20kHz, the human hearing range, the upper limit of which is our
target. Also, the peak-peak voltage outputted is within our desired
specifications, as we’ll see further.

### Audio Signal

A *python* script that receives the hexadecimal string with the
instructions and parses it into binary was written. Next, this bit-data
is fed into a function that generates a *wav* file, using *python’s
wave* module. This is accomplished by sampling a 20kHz sine wave at
198kHz sampling rate, for the right durations
(Fig.<a href="#fig:bitdata" data-reference-type="ref"
data-reference="fig:bitdata">2</a>) and appending it to our *Wave_write*
object. Finally, the *wav* file is saved and a macro is invoked to play
it and transmit the control data.

Looking at the output signal
(Fig.<a href="#fig:osc0V-" data-reference-type="ref"
data-reference="fig:osc0V-">[fig:osc0V-]</a>), the bit-data structure is
clearly identifiable (1110111 on this example). Furthermore, upon closer
examination of the carrier signal (Fig.
<a href="#fig:osc0V+" data-reference-type="ref"
data-reference="fig:osc0V+">[fig:osc0V+]</a>), three notable
observations come to light:

-   It is 512*m**V* peak-peak, which indeed is within our desired range;

-   It is 19.86kHz, which is also within our desired range and 0.7%
    deviated from the expected 20kHz;

-   It’s arithmetic mean is 1.41*m**V*, which, given the sinusoidal
    nature of the signal, results in a near-zero voltage centering.

### Bias Tee

As mentioned previously, DiSEqC runs both the 12V DC and the control
signal on the same coaxial cable. In order to set this DC bias, a *bias
tee* circuit was employed
(Fig.<a href="#fig:biastee" data-reference-type="ref"
data-reference="fig:biastee">[fig:biastee]</a>).

<div class="circuitikz">

(0,2) to \[V, l= 12*V*\] (0,4) to \[L, l= 1*m**H*, -\*\] (4,4) to
\[short, -o\] (5, 4) (0,2) to (0,1) node\[ground\] (0,2) to \[short,
\*-\*\] (2, 2) to \[C, l\_ = 300*n**F*\] (2, 0) to \[vsourcesin, l\_
=*C**o**n**t**r**o**l* *S**i**g**n**a**l*\] (4,0) to \[C, l\_ =
300*n**F*\] (4, 2) to \[short, -\*\] (4,4) (2,2) to \[short, -o\] (5, 2)
(5,2) to \[open, v^\>=*C**o**n**t**r**o**l* *S**i**g**n**a**l* + 12*V*\]
(5,4);

</div>

Inspecting the signal on
Fig.<a href="#fig:osc12V" data-reference-type="ref"
data-reference="fig:osc12V">[fig:osc12V]</a>, it looks identical to the
one on Fig.<a href="#fig:osc0V" data-reference-type="ref"
data-reference="fig:osc0V">[fig:osc0V]</a>, the only difference being
the 12*V* DC offset (the mean is now 12.1*V* instead of 1.41*m**V*),
just as intended.

We can calculate the impedance of the capacitor, *X*<sub>*C*</sub>, and
the impedance of the inductor, *X*<sub>*L*</sub> through the following:

$$X_C = \\frac{1}{w C} = \\frac{1}{2\\pi f C} = \\frac{1}{2\\pi \\cdot 20kHz \\cdot 300nF} = 26.5\\Omega
  \\label{eq:impedanceC}$$

*X*<sub>*L*</sub> = *w**L* = 2*π**f**L* = 2*π* ⋅ 20*k**H**z* ⋅ 1*m**H* = 125.7*Ω*
Where *f* is the signalling frequency, 20*k**H**z*.


