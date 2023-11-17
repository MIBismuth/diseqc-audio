<div class="titlepage">

<div class="flushleft">

![image](IST_A_CMYK_POS.eps)

</div>

*Scientific Project*  
<span class="smallcaps">**Automatic Control of a 2 Axis Parabolic Mirror
for a Solar Light Concentrator**</span>

José Duarte Lopes  
Supervisors:  
Horácio  
Fernandes

</div>

# Introduction

The sun is the single most important energy source humans and (pretty
much) all life forms on Earth have at their disposal.

For centuries we have garnered the sun’s energy through indirect means,
be it by burning fossil fuels, like coal or oil, burning wood, or by
harnessing wind and hydroelectric power. Only more recently have we
begun to develop ways to utilize solar power by more direct means. Solar
Light Concentrators are one of them.

A Solar Light Concentrator is, like the name implies, a device that can
*concentrate*, i.e. focus, incident solar light on a large area down to
a smaller area. This process generates large amounts of heat, that can
be channeled to vaporize water, generating steam. This steam can drive a
turbine, ultimately producing energy. The system that is used to heat
the water, which circulates on a brass cylinder, is a heat machine.

One of the disadvantages of a such a device is that, in order to keep a
stable focus, it becomes imperative for it to be able to continuously
and precisely track the sun’s apparent motion throughout the day. This
requires careful development and deployment of a system capable of
rotating the device in two distinct axis, as well as a live feedback
system that communicates with the mechanical part and ensures optimal
positioning at all times.

The work I’ve developed for *PIC* mainly concerns the assembly and
control of the two positioners systems generating angular motion.

# Right Ascension Positioner

The first big milestone in this project was to control the right
ascension positioner, a satellite dish positioner
(Fig.<a href="#fig:DP" data-reference-type="ref"
data-reference="fig:DP">1</a>) through a raspberry pi micro controller.
The positioner can be controlled by DiSEqC commands, so the
comprehension of this protocol is primary to our objectives.

<figure>
<img src="figures/Ascension/motor1.jpg" id="fig:DP" style="width:45.0%"
alt="DiSEqC Satellite Positioner. It can be controlled with DiSEqC commands, whose control signal runs on the same coaxial cable as the 12V DC to power the motor and all the electronics" />
<figcaption aria-hidden="true">DiSEqC Satellite Positioner. It can be
controlled with DiSEqC commands, whose control signal runs on the same
coaxial cable as the 12V DC to power the motor and all the
electronics</figcaption>
</figure>

## DiSEqC Protocol

"The DiSEqC system is a communication bus between satellite receivers
and satellite peripheral equipment". It works by sending both the
12 ± 1*V* DC, to power the motor and all the electronics, as well as a
22*k**H**z*(±20%) control signal, which should be 650 ± 250*m**V*
peak-peak, on the same coaxial cable . Firstly, we need to understand
how to construct the actual message that needs to be delivered.

### Data-Bit Signalling

Starting from the smallest element of digital information, data-bit
signalling "uses base-band timings of (500±100)*μ**s* for a one-third
bit PWK (Pulse Width Keying) coded signal period on a nominal
22*k**H**z*(±20%) carrier" . This means that:

-   Bit *0* - (1.0±0.2)*m**s* tone, nominally 22 cycles, followed by
    (0.5±0.1)*m**s* of silence

-   Bit *1* - (0.5±0.1)*m**s* tone, nominally 11 cycles, followed by
    (1.0±0.2)*m**s* of silence

Or, as shown on the following diagram (Fig.
<a href="#fig:bitdata" data-reference-type="ref"
data-reference="fig:bitdata">2</a>)

<figure>
<img src="figures/Ascension/diseqc_modulation.png" id="fig:bitdata"
style="width:50.0%"
alt="DiSEqC Modulation Scheme (source: ). The ’0’ data bit is comprised of 1ms of carrier frequency, followed by 0.5ms of silence, while the ’1’ data bit is the opposite." />
<figcaption aria-hidden="true">DiSEqC Modulation Scheme (source: <span
class="citation" data-cites="diseqc"></span>). The ’0’ data bit is
comprised of <span class="math inline">1<em>m</em><em>s</em></span> of
carrier frequency, followed by <span
class="math inline">0.5<em>m</em><em>s</em></span> of silence, while the
’1’ data bit is the opposite.</figcaption>
</figure>

### Message Data Format

DiSEqC messages consist of one or more bytes, with each bit as defined
in the previous section, and each byte followed by an odd parity bit .
The commands from the master are structured as follows:

<div id="tab:command">

| Framing | P   | Address | P   | Command | P   | Data | P   |
|:--------|:----|:--------|:----|:--------|:----|:-----|:----|

Basic DiSEqC command structure

</div>

To move the positioner to a given angle, the command we want to send is:

<div id="tab:diseqcmove">

| E1  | P   | 31  | P   | 6E  | P   | E/D XX.X | P   |
|:----|:----|:----|:----|:----|:----|:---------|:----|

Command move to position (hex)XX.X

</div>

Looking at what each of those blocks represent:

-   *P* - Odd Parity Bit;

-   *E1* - Framing signalling Command from Master, No reply required,
    Repeated transmission;

-   *31* - Address of Polar/Azimuth Positioner;

-   *6E* - Command Drive Motor to Angular Position;

-   *E/D XX.X* - *E* denotes "east of 0" and *D* "west of 0", while
    *XX.X* is the target angle, in hexadecimal.

Note that we can specify angles to the motor up to 1/16 .

We now have all the information needed to control the positioner!

## Raspberry Pi Implementation

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

# Declination Positioner

To drive the Declination Positioner, an electric AC motor, like the ones
found on automatic gates, was used
(Fig.<a href="#fig:ACMotor" data-reference-type="ref"
data-reference="fig:ACMotor">3</a>).

<figure>
<img src="figures/Declination/ACmotor" id="fig:ACMotor"
style="width:45.0%"
alt="AC electric motor used as Declination Positioner. As the motor rotates, a screw drives an element forward in a linear fashion." />
<figcaption aria-hidden="true">AC electric motor used as Declination
Positioner. As the motor rotates, a screw drives an element forward in a
linear fashion.</figcaption>
</figure>

### Controlling the Motor

The particular model used was a Permanent Split Capacitor (PSC) Motor.
In order to be powered by a residential single-phase power supply, these
motors use two windings: one connected directly to the power supply and
another connected via a capacitor. The capacitor generates a phase
difference between the main and secondary windings, causing the peak
magnetic field to alternate between them, producing the necessary torque
to start the rotation.

By switching which winding is connected to the power supply, it is
possible drive the motor in reverse. This is great because it allows us
to not only turn the motor on and off, but also control the direction of
the motion using a microcontroller and a simple two relay module setup:
one relay to turn on/off and another to switch windings. The implemented
circuit can be seen on
Fig.<a href="#fig:schematicdecline" data-reference-type="ref"
data-reference="fig:schematicdecline">[fig:schematicdecline]</a>.

<div class="circuitikz">

(1,0) rectangle (3.8,4); at (2.5,4.3) Two Relay Module; (1.5,2.2)
rectangle (3.5,3.8); at (2.5,3) *R**e**l**a**y*\_1; (1.5,0.2) rectangle
(3.5,1.8); at (2.5,1) *R**e**l**a**y*\_2; (0.5,3.5) node\[left, font =
\] GND – (1.,3.5); (0.5,2.5) node\[anchor = south, font = \]
*I**N*<sub>1</sub> – (1.,2.5); (0.5,1.5) node\[anchor = south, font = \]
*I**N*<sub>2</sub> – (1.,1.5); (0.5,0.5) node\[left, font = \] VCC –
(1.,0.5);

(0.3,2.5) node\[left, font = \] GPIO1 – (1.,2.5); (0.3,1.5) node\[left,
font = \] GPIO2 – (1.,1.5);

(4.5,3.6) node\[anchor=south, font=\] *N**C*<sub>1</sub> – (3.5,3.6);
(4.5,3.0) node\[anchor=south, font=\] *C**O**M*<sub>1</sub> – (3.5,3.0);
(4.5,2.4) node\[anchor=south, font=\] *N**O*<sub>1</sub> – (3.5,2.4);

(4.5,1.6) node\[anchor=south, font=\] *N**C*<sub>2</sub> – (3.5,1.6);
(4.5,1) node\[anchor=south, font=\] *C**O**M*<sub>2</sub> – (3.5,1);
(4.5,0.4) node\[anchor=south, font=\] *N**O*<sub>2</sub> – (3.5,0.4);

(4.5, 2.4) – (5., 2.4); (5., 2.4) – (5., 2.2) to\[crossing\] (5., 1);
(4.5, 1) – (5., 1);

(5.5, 3) node\[right\]*L**i**v**e* (220*V*) – (4.5, 3); (4.5, 0.4) –
(5.5, 0.4); (4.5, 1.6) – (5.5, 1.6); (5.5, 0.4) to\[ospst,
l\_=*S*<sub>2</sub>\] (6, 0.4); (5.5, 1.6) to\[ospst,
l=*S*<sub>1</sub>\] (6, 1.6); (6.5, 0.4) to\[short, -\*\] (6, 0.4);
(6.5, 0.4) – (6.5, -1) – (6, -1); (6, 1.6) to\[short, \*-\] (7, 1.6) –
(7, -2) – (6, -2) to \[C, l\_=1.41*μ**F*, \*-\*\] (6, -1);

(4, -1.5) node\[elmech\](motor)M; (4, -1) – (6, -1); (4, -2) – (6, -2);
(motor.left) – (2, -1.5) node\[left\]*N**e**u**t**r**a**l*;

</div>

Notice the normally closed switches *S*<sub>1</sub> and *S*<sub>2</sub>.
These function as limit switches: when the positioner reaches it’s
minimum or maximum position, these will open the circuit, shutting down
the power to the motor, stopping it, thus preventing unwarranted damage;
the only way the motor can ever move again is by toggling
*R**e**l**a**y*\_2 and reversing.

However, there remains a requirement to communicate to the Raspberry Pi
that the limit switches were activated. To implement this functionality,
a dual pull-up switch system was employed
(Fig.<a href="#fig:rpisw" data-reference-type="ref"
data-reference="fig:rpisw">[fig:rpisw]</a>). It’s critical that these
are positioned in parallel to *S*<sub>1</sub> and *S*<sub>2</sub>, in
such a way that they are always closed prior to them. Otherwise, the
system could physically shut down and stop all motion, but the
microcontroller would never receive that information, confining the
system to be stuck in that state indefinitely.

<div class="circuitikz">

(0,0) node\[spdt,xscale=-1,anchor=in\] (sw) (sw.in) node\[right\] GPIO
(sw.out 2) – ++(0,-0.5) node\[ground\] ; (sw.out 1) to
\[R,l=*R*<sub>pull-up</sub>\] ++(0,1.5) coordinate (A); (A) – ++(0,0.2)
node\[vcc\] *V*<sub>cc</sub>(5*V*);

</div>

### Designing and Implementing the Mechanical Structure

It is necessary to translate the linear motion of the motor, *x*, into a
change in the angle of the pole, *α*. To accomplish that, a system like
the one on Fig.<a href="#fig:struct" data-reference-type="ref"
data-reference="fig:struct">[fig:struct]</a> was used.

<div class="center">

</div>

The pole is fixed on a hinge on Point *A*. Then, an arm of length
*d*<sub>4</sub> is attached to the pole on Point *B* and to the moving
part of the gate motor on Point *C*. We can see that as *x* moves along
it’s axis, it drags the pole with it, changing the value of *α*.

It is fairly simple to obtain *x*(*α*).

First,

$$\\label{eq:xa1}
\\begin{aligned}
d_3 \\sin(\\alpha) &= h_1 \\\\
d_3 \\cos(\\alpha) &= s_1 \\\\
d_4 \\sin(\\beta) &= h_1 + d_2 \\\\
d_4 \\cos(\\beta) &= (d_1 - s_1) + x \\\\
\\end{aligned}$$

Rearranging the terms,

$$\\label{eq:xa2}
\\begin{aligned}
d_4 \\sin(\\beta) &= d_3 \\sin(\\alpha) + d_2 \\\\
d_4 \\cos(\\beta) &= d_1 - d_3 \\cos(\\alpha) + x
\\end{aligned}$$

Finally,
$$\\label{eq:xa3}
\\begin{aligned}
\\beta &= \\arcsin\\left(\\frac{d_3 \\sin(\\alpha) + d_2}{d_4}\\right) \\\\
x &= d_4 \\sqrt{1 - \\left(\\frac{d_3 \\sin(\\alpha) + d_2}{d_4}\\right)^2} + d_3 \\cos(\\alpha) - d_1
\\end{aligned}$$

Now, determining the optimal values of our four free parameters,
*d*<sub>1</sub> through *d*<sub>4</sub>, is no trivial task. However, we
can apply some physical constraints to our model:

-   *x*<sub>*M**A**X*</sub> ≤ 30*c**m* - the *x* range of our linear
    positioner;

-   *α*<sub>*M**A**X*</sub>- *α*<sub>*M**I**N*</sub> ≥ 47- our model has
    to be able to match the sun’s declination throughout the year;

-   *β*<sub>*M**I**N*</sub> ≥ 20- any lower than this would apply
    unnecessary strain to our structure;

Subsequently, by taking these constraints and applying them to a CAD
model (Fig.<a href="#fig:cad" data-reference-type="ref"
data-reference="fig:cad">4</a>), the free parameters were determined.
Following these (or trying to), the physical structure itself was
constructed (Fig.<a href="#fig:structure" data-reference-type="ref"
data-reference="fig:structure">5</a>).

<div class="center">

<figure>
<img src="figures/Declination/CAD.png" id="fig:cad" style="width:50.0%"
alt="CAD model used to help determine free parameters." />
<figcaption aria-hidden="true">CAD model used to help determine free
parameters.</figcaption>
</figure>

</div>

<div class="center">

<figure>
<img src="figures/Declination/structure.jpg" id="fig:structure"
style="width:50.0%"
alt="Mechanical Structure Built. Notice the robust arm linking the linear positioner to the pole which will hold the Parabolic Mirror. It is this arm that allows for control of the angle \alpha." />
<figcaption aria-hidden="true">Mechanical Structure Built. Notice the
robust arm linking the linear positioner to the pole which will hold the
Parabolic Mirror. It is this arm that allows for control of the angle
<span class="math inline"><em>α</em></span>.</figcaption>
</figure>

</div>

All of the parameters, target and real, are compiled on
Tab.<a href="#tab:valuesL" data-reference-type="ref"
data-reference="tab:valuesL">3</a> and
<a href="#tab:valuesA" data-reference-type="ref"
data-reference="tab:valuesA">4</a>.

<div id="tab:valuesL">

|        | *d*<sub>1</sub>                  | *d*<sub>2</sub> | *d*<sub>3</sub> | *d*<sub>4</sub> | *x*<sub>*M**A**X*</sub> |
|:-------|:---------------------------------|:----------------|:----------------|:----------------|:------------------------|
| Target | 44.0                             | 5.8             | 28.0            | 51.6            | 30                      |
| Real   | 47.0                             | 9.8             | 28.0            | 52.2            | 29.5                    |
|        | *D**i**s**t**a**n**c**e*(*c**m*) |                 |                 |                 |                         |

Linear Parameters

</div>

<div id="tab:valuesA">

|        | *α*<sub>*M**I**N*</sub> | *α*<sub>*M**A**X*</sub> | *Δ**α* |
|:-------|:------------------------|:------------------------|:-------|
| Target | 25.0                    | 80.0                    | 55.0   |
| Real   | 15.0                    | 72.5                    | 57.5   |
|        | *D**e**g**r**e**e* ()   |                         |        |

Angle Parameters

</div>

As observed in the results, *d*<sub>1</sub> and *d*<sub>2</sub> were off
from the target by the larges amount, *d*<sub>2</sub> being 69.0% larger
than the target. However, we still get an *α* range of 57.5, and even
capping *α*<sub>*M**I**N*</sub> at 25 for structural stability and
longevity, we still hit the necessary 47 range.

### Calibration

Keeping in mind our primary objective of accurately positioning the
device, the following procedure obviously entails measuring real world
results and comparing them to the physical model. In other words, we
need to obtain *x*<sub>*r**e**a**l*</sub>(*α*<sub>*r**e**a**l*</sub>).

Measurements of the angle, *α*, were made to multiple positions of *x*.
These points were then plotted and fitted against
Eq.<a href="#eq:xa3" data-reference-type="ref"
data-reference="eq:xa3">[eq:xa3]</a>
(Fig.<a href="#fig:xaplot" data-reference-type="ref"
data-reference="fig:xaplot">6</a>).

<figure>
<embed src="figures/Declination/xafit.pdf" id="fig:xaplot"
style="width:45.0%" />
<figcaption aria-hidden="true">Plot of <span
class="math inline"><em>x</em>(<em>α</em>)</span> and Fit Results to
Eq.<a href="#eq:xa3" data-reference-type="ref"
data-reference="eq:xa3">[eq:xa3]</a>. Notice the experimental data is
very well adjusted to the physical model: <span
class="math inline">$\frac{\chi^2}{ndf} = 1.33$</span>; linear
parameters measured (Tab.<a href="#tab:valuesL"
data-reference-type="ref" data-reference="tab:valuesL">3</a>) similar to
fit parameters.</figcaption>
</figure>

An analysis of the results of
Fig.<a href="#fig:xaplot" data-reference-type="ref"
data-reference="fig:xaplot">6</a> reveal that our results corroborate
the physical model: $\\frac{\\chi^2}{ndf} = 1.33$, which is close to 1;
the linear parameters measured
(Tab.<a href="#tab:valuesL" data-reference-type="ref"
data-reference="tab:valuesL">3</a>) are all encompassed within the fit
parameters and their respective uncertainties.

Now, all that is missing is achieving precise movement of the linear
positioner to reach position *x*. Ideally, this would be done using an
encoder that would count the exact number of rotations of the motor.
However, we can get pretty good results simply using humble time based
control, i.e, turning the motor On some *δ**t*(*α*): assuming the
positioner velocity, *ẋ*, to be constant,
$\\dot{x} = \\frac{x - x_0}{\\delta t}$, *x* is trivially
*x*<sub>0</sub> + *ẋ**δ**t*.

We can get an accurate measurement of *ẋ* by employing the Digital Limit
Switches (Fig.<a href="#fig:rpisw" data-reference-type="ref"
data-reference="fig:rpisw">[fig:rpisw]</a>) and calculating the time it
takes for the positioner to transverse it’s entire length of motion. The
results obtained were (22.45±0.10)*s* going from 0 to 29.5*c**m* and
(22.55±0.10)*s* on the opposite way, which comes to
*ẋ*<sub>*u**p*</sub> = 1.308*c**m* ⋅ *s*<sup>−1</sup> and
*ẋ*<sub>*d**o**w**n*</sub> = 1.314*c**m* ⋅ *s*<sup>−1</sup>.

Finally:
$$\\delta t (\\alpha) = \\frac{x(\\alpha) - x(\\alpha_0)}{\\dot{x}\_{up/down}}
\\label{eq:ta}$$

Where *x*(*α*) is the equation obtained fron the Fit Results on
Fig.<a href="#fig:xaplot" data-reference-type="ref"
data-reference="fig:xaplot">6</a> and *α*<sub>0</sub> is the current
angle.

Now that we have derived the fundamental equation
(Eq.<a href="#eq:ta" data-reference-type="ref"
data-reference="eq:ta">[eq:ta]</a>), we are able to assess the accuracy
of our positioner through testing
(Fig.<a href="#fig:atest" data-reference-type="ref"
data-reference="fig:atest">7</a>).

<div class="center">

<figure>
<embed src="figures/Declination/alphatest.pdf" id="fig:atest"
style="width:50.0%" />
<figcaption aria-hidden="true">Plot of the Target Angle against Real
Measure. Notice the perfect correlation between the two from 38 until
70. From 20 to 36, we can observe a linear systematic
error.</figcaption>
</figure>

</div>

Upon analyzing the results, it is evident that a remarkable
correspondence exists between the Target Angle and the Real Angle within
the range of 38  to 70. In this range, the alignment is perfect (which
means it’s at least as good as a simple protractor and my naked eye).

However, within the range of 20  to 36, a systematic error becomes
apparent. There is a linear trend observed, where the measured angles
consistently deviate from the target angles. At 20, the recorded angle
exhibits a negative bias of approximately -1, gradually converging to
perfect correspondence at 38. This systematic error can be accounted for
very easily.

We can conclude that the accuracy of the system is at least as good as
the accuracy of the instrument utilized for angle measurements, which in
this case was a simple protractor. Therefore, until more refined
measurements are taken, the inherent error of this system remains
consistent at approximately  ± 0.5 , mirroring the margin of error
associated with the protractor itself.

# Real World Performance

## Is Our System Even Good Enough?

The focus point of the Parabolic Mirror was measured by burning a mark
on a piece of wood (Fig.<a href="#fig:burn" data-reference-type="ref"
data-reference="fig:burn">8</a>).

<figure>
<img src="figures/RealWorld/burn.jpg" id="fig:burn" style="width:45.0%"
alt="By placing a piece of wood directly on the focus point of the Parabolic Mirror, it immediately gets burned, leaving a charred mark." />
<figcaption aria-hidden="true">By placing a piece of wood directly on
the focus point of the Parabolic Mirror, it immediately gets burned,
leaving a charred mark.</figcaption>
</figure>

The diameter of the focal point measured is approximately 1.5*c**m*.
Furthermore, the target we wish to hit is a circumference 5*c**m*
across, and less than 50*c**m* away from the mirror. This means that our
system has to be accurate enough to focus the solar light within
1.75*c**m* of the center of the target.

We can calculate the max error our system can support.

<div class="center">

</div>

On Fig.<a href="#fig:maxerror" data-reference-type="ref"
data-reference="fig:maxerror">[fig:maxerror]</a>, we can observe that
*X* is the center of the maximum allowed focus position. *X* has
coordinates $\\sqrt(\\frac{1.75^2}{2}) = 1.237cm$. The max angular
error, *δ**α*<sub>max</sub>, is:

$$\\label{eq:error}
\\begin{aligned}
\\tan(\\delta\\alpha\_{\\text{max}}) &= \\frac{1.237}{50} \\nonumber \\\\
\\Rightarrow \\delta\\alpha\_{\\text{max}} &= \\arctan\\left(\\frac{1.237}{50}\\right) = 1.42^\\circ
\\end{aligned}$$

Therefore, the maximum angular error of our positioners amounts to 1.42.
In our previous analysis, we observed an error range of  ± 0.5 for the
declination positioner, and the DiSEqC positioner exhibits significantly
higher accuracy. This implies that our system meets the required
criteria since the error of the positioners falls below the maximum
permissible error limit.

So, indeed, our system is good enough!

## Bringing it All Together

The time has finally come to write the control sequence of our machine.
For the sake of brevity, the code won’t be discussed in detail in this
report, being confined in all it’s uncensored glory to the Appendix,
reserved to be gazed only by the most curious among the readers.

The basic structure is the following:

-   Two Classes were employed, *RightAscension* and *Declination*, each
    implementing methods to control the positioner bearing the same
    name;

-   The *main* function performs a basic setup and calls the two loop
    threads, *positionersControlLoop* and *userInputLoop*;

-   *positionersControlLoop* continuously updates the Right Angle
    positioner based on the solar rate and the time passed, aswell as
    user inputed offsets; updates the Declination based on the
    declination of the sun and user inputted offsets.

-   *userInputLoop* prompts the user for offsets, useful for calibration
    purposes.

In the future, the program could easily be extended with another thread
that registers the offsets from the feedback system, in a similar
fashion to *userInputLoop*.

## The Big Experiment

The device was, conclusively, taken outdoors for testing purposes
(Fig.<a href="#fig:outdoors" data-reference-type="ref"
data-reference="fig:outdoors">9</a>). Following an initial calibration,
it was operated for a duration of 20 minutes, during which the focal
point of the concentrator was directed towards a piece of brass
(Fig.<a href="#fig:brass" data-reference-type="ref"
data-reference="fig:brass">10</a>).

<figure>
<img src="figures/RealWorld/outside.png" id="fig:outdoors"
style="width:45.0%"
alt="Solar Concentrator being tested outside in sunny conditions. The device was successfully able to track the suns movement. A piece of the equipment used to hold the brass block in focus melted (notice the smoke)." />
<figcaption aria-hidden="true">Solar Concentrator being tested outside
in sunny conditions. The device was successfully able to track the suns
movement. A piece of the equipment used to hold the brass block in focus
melted (notice the smoke).</figcaption>
</figure>

<figure>
<img src="figures/RealWorld/brass.jpeg" id="fig:brass"
style="width:45.0%"
alt="Brass Block, 5cm in diameter, used as target of the experiment. It reached a maximum superficial temperature of 357.8C." />
<figcaption aria-hidden="true">Brass Block, <span
class="math inline">5<em>c</em><em>m</em></span> in diameter, used as
target of the experiment. It reached a maximum superficial temperature
of 357.8C.</figcaption>
</figure>

Throughout the entire experiment, the Right Angle positioner
consistently tracked the sun’s position with precision, maintaining
focus without any loss. The structural integrity of the device was also
put to the test due to the presence of wind perpendicularly striking the
parabolic mirror, to no effect on the verdict. This successful outcome
signifies a notable achievement.

However, the experiment had to be prematurely concluded due to the
equipment’s inability to withstand the extreme heat generated, i.e, the
brass block holder melted (notice the smoke on
Fig.<a href="#fig:outdoors" data-reference-type="ref"
data-reference="fig:outdoors">9</a>). Nevertheless, the results obtained
were highly favorable, with the recorded temperature on the brass
reaching 357.8C, which is hot enough to boil water (it even proved
itself hot enough to light a cigarette on fire).

# Final Remarks

The initial objective of constructing a solar tracking device capable of
precise monitoring of solar movement has been successfully accomplished.
The constructed device has exhibited a surprising level of accuracy,
particularly on the declination axis, with an error margin of no more
than 0.5 degrees. Furthermore, it surpasses this level of precision on
the right angle axis, maintaining a consistently stable focal point on
the designated target. Experimentally, the Concentrator has demonstrated
considerable efficacy in this regard as well.

Additionally, in terms of heat generation, the obtained outcomes have
shown great promise, having achieved an impressive focal temperature of
357.8 degrees Celsius within a duration of 20 minutes of exposure.

Nevertheless, further examination is necessary to validate the long-term
accuracy of this setup under varying weather conditions. Specifically,
it is crucial to implement and assess the performance of the feedback
system while integrating it with the energy generator itself. As it
currently stands, the Concentrator exhibits effectiveness in generating
high temperatures.

Although there is still a significant distance to cover before this
technology becomes a viable solution for green electricity production,
we have hopefully demonstrated its potential for future development and
advancement, envisioning a more sustainable world.

# Appendix

    import asyncio
    import datetime
    import threading
    from declass import Declination
    from raclass import RightAngle
    from pysolar import solar
    import time

    async def positionersControlLoop(ra, dec):
        # Tecnicos geographic coordinates (latitude and longitude)
        latitude = 38.7355585
        longitude = -9.1395432
        solar_rate = 360 / (24 * 60 * 60)
        while True:
            raangle = (time.time() - ra.time_created) * solar_rate
            # raangle dd= solar.get_azimuth(latitude, longitude, date) - 280
            offsetDec = dec.offset
            moveRightAngle = asyncio.create_task(ra.goToAngle(raangle))
            moveDeclination = asyncio.create_task(dec.moveAngle(offsetDec))
            await moveRightAngle
            await moveDeclination

    async def userInputLoop(ra, dec):
        while True:
            # Prompt the user for angle offsets
            offset1 = float(input("Enter offset for right angle: "))
            offset2 = float(input("Enter offset for declination angle: "))

            ra.setOffset(offset1)
            dec.setOffset(offset2)

    def runPositionersControlLoop(ra, dec):
        asyncio.run(positionersControlLoop(ra, dec))

    def runUserInputLoop(ra, dec):
        asyncio.run(userInputLoop(ra, dec))

    async def main():
        ra = RightAngle()
        dec = Declination()
        print("Created Positioner Objects")
        print("Doing Setup")
        await dec.goToAngleFromTop(40)
        # Create and start the threads
        motor_thread = threading.Thread(target=runPositionersControlLoop, args=(ra, dec))
        user_input_thread = threading.Thread(target=runUserInputLoop, args=(ra, dec))

        motor_thread.start()
        user_input_thread.start()

    if __name__ == "__main__":
        # run main
        asyncio.run(main())

    import wave
    import math
    import asyncio
    import time


    class RightAngle:
        def __init__(self):
            self.sample_rate = 198000
            self.num_channels = 1
            self.sample_width = 2
            self.amplitude = 32767
            self.freq_hz = 20000
            self.num_sine_samples = int(self.sample_rate * 0.002)
            self.sine_samples = self.generate_sine_samples()
            self.offset = 0
            self.position = 0
            self.time_created = time.time()

        def angle_to_hex(self, angle):
            hex_string = "E" if angle <= 0 else "D"
            angle = abs(round(angle, 1))
            angle_int = int(angle)
            angle_frac = int((angle - angle_int) * 16)
            return hex_string + (hex(angle_int)[2:] + hex(angle_frac)[2:]).upper().zfill(3)

        def bit_encoder(self, hex_input):
            byte_input = bytes.fromhex(hex_input)
            for byte in byte_input:
                binary_string = bin(byte)[2:].zfill(8)
                num_ones = binary_string.count("1")
                parity_bit = "0" if num_ones % 2 == 0 else "1"
                binary_string += parity_bit
                for bit in binary_string:
                    yield int(bit)

        def generate_sine_samples(self):
            sine_samples = []
            for j in range(self.num_sine_samples):
                sample = int(
                    self.amplitude
                    * math.sin(2 * math.pi * self.freq_hz * j / self.sample_rate)
                )
                sine_samples.append(sample)
            return sine_samples

        async def goToAngle(self, angle):
            hex_input = "E0316E" + self.angle_to_hex(angle + self.offset)
            self.position = angle

            with wave.open("binary_wave.wav", "wb") as wave_file:
                wave_file.setnchannels(self.num_channels)
                wave_file.setsampwidth(self.sample_width)
                wave_file.setframerate(self.sample_rate)

                for bit in self.bit_encoder(hex_input):
                    if bit:
                        for i in range(int(self.sample_rate * 0.0006)):
                            wave_file.writeframesraw(
                                self.sine_samples[i].to_bytes(
                                    2, byteorder="little", signed=True
                                )
                            )
                        for i in range(int(self.sample_rate * 0.001)):
                            wave_file.writeframesraw(b"\x00\x00")
                    else:
                        for i in range(int(self.sample_rate * 0.0011)):
                            wave_file.writeframesraw(
                                self.sine_samples[i].to_bytes(
                                    2, byteorder="little", signed=True
                                )
                            )
                        for i in range(int(self.sample_rate * 0.0005)):
                            wave_file.writeframesraw(b"\x00\x00")

                for i in range(int(self.sample_rate * 0.006)):
                    wave_file.writeframesraw(b"\x00\x00")

            process = await asyncio.create_subprocess_exec(
                "play",
                "-q",
                "binary_wave.wav",
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.STDOUT,
            )

            await process.wait()
            wave_file.close()

        def setOffset(self, angle):
            self.offset += angle


    async def main():
        ra = RightAngle()
        await ra.goToAngle(float(input("Angle: ")))


    if __name__ == "__main__":
        asyncio.run(main())

    import pifacedigitalio
    import time
    import asyncio
    from math import sqrt, cos, sin, pi


    class Declination:
        def __init__(self):
            self.pifacedigital = pifacedigitalio.PiFaceDigital()

            self.x_pos = 0
            self.x_err = 0
            self.alpha = 0
            self.alpha_err = 0
            self.updown = 0  # up = 0, down = 1
            self.moving = 0  # stop = 0, move = 1
            self.timeDown = 22.45
            self.timeUp = 22.55
            self.offset = 0

        async def move(self, dir):  # We do it this way to avoid burnuin the relay
            self.pifacedigital.output_pins[6].value = 0
            await asyncio.sleep(0.4)
            self.pifacedigital.output_pins[7].value = dir
            await asyncio.sleep(0.4)
            self.pifacedigital.output_pins[6].value = 1

        def stop(self):
            self.pifacedigital.output_pins[6].value = 0

        def x(self, angle):
            return (
                52.87 * sqrt(1 - ((27.24 * sin(angle * pi / 180) + 11.77) / 52.87) ** 2)
                + 27.24 * cos(angle * pi / 180)
                - 46.22
            )

        async def goAllTheWay(self, dir):
            if dir:  # move down
                if self.pifacedigital.input_pins[0].value == 1:
                    print("Already all the way down")
                else:
                    await self.move(dir)
                    open = 1
                    while open:
                        if self.pifacedigital.input_pins[0].value == 1:
                            await asyncio.sleep(0.002)
                            if self.pifacedigital.input_pins[0].value == 1:
                                open = 0
                                self.stop()
                                print("All the way Down!")

            else:  # move up
                if self.pifacedigital.input_pins[1].value == 1:
                    print("Already all the way up")
                else:
                    await self.move(dir)
                    open = 1
                    while open:
                        if self.pifacedigital.input_pins[1].value == 1:
                            await asyncio.sleep(0.002)
                            if self.pifacedigital.input_pins[1].value == 1:
                                open = 0
                                self.stop()
                                print("All the way Up!")

        async def calibration(self):
            await self.goAllTheWay(0)
            await asyncio.sleep(0.5)
            time1 = time.time()
            await self.goAllTheWay(1)
            self.timeDown = time.time() - time1
            print(f"time down = {self.timeDown}")

            await asyncio.sleep(0.5)
            time1 = time.time()
            await self.goAllTheWay(0)
            self.timeUp = time.time() - time1
            print(f"time up = {self.timeUp}")

        async def goToAngleFromTop(self, angle):
            if angle < 20 or angle > 70:
                print("Angle must be between 70 and 20 degrees")
            else:
                await self.goAllTheWay(0)
                await asyncio.sleep(0.5)
                time_moving = self.x(angle) * self.timeDown / 29.5
                print(time_moving)
                await self.move(1)
                await asyncio.sleep(time_moving)
                self.stop()
                self.alpha = angle

        async def disconnect(self):
            self.pifacedigital.output_pins[6].value = 0
            await asyncio.sleep(0.5)
            self.pifacedigital.output_pins[7].value = 0

        def setOffset(self, angle):
            self.offset += angle

        async def moveAngle(self, angle):
            if angle == 0:
                pass

            else:
                x = self.x(angle + self.alpha) - self.x(self.alpha)
                if x > 0.5:
                    time_moving = x * self.timeDown / 29.5
                    print(time_moving)
                    await self.move(1)
                    await asyncio.sleep(time_moving)
                    self.stop()
                    self.alpha += angle
                elif x < -0.5:
                    time_moving = -x * self.timeUp / 29.5
                    await self.move(0)
                    await asyncio.sleep(time_moving)
                    self.stop()
                    self.alpha += angle
                else:
                    print("offset must be bigger than 0.5cm")
                self.offset = 0
