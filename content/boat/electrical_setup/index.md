+++
  title = "Electrical setup"
  description = "How we setup the boat's electrical system to support off-grid living"
  weight = 4
  [cover]
    image = "integrel_epower.jpg" 
    alt = "map"
    caption = "Integrel generator"
    relative = true # Tells PaperMod to look inside the current post folder
+++

In our everyday lives, we take for granted unlimited power from the AC outlets, endless water from the tap, toilets that flush
and take the waster away *somewhere*.  None of that applies at sea, so enabling the boat to off grid for weeks on end takes some careful 
thought.

One of the biggest changes recent years has been the shift from generator + AGM batteries to solar + Lithium (Lithium Iron Phosphate or LiFePO)
batteries.  The increased capacity of Lithium batteries enables boats to run energy hogging devices like electric ovens, water makers, and 
even air con, without having a generator running constantly.  Ideally, solar energy collected during the day can provide the bulk of
the boats electrical needs, but you need a fallback in case of a series of cloudy days or some unexpected increase in energy needs.

Normally, a generator is used to charge the batteries, but it's weight and another engine to maintain.  As we were sorting out the options 
with FP, I became interested in a system developed by Integrel Solutions (based in UK) that works as a "smart" alternator attached to
your engine.  Unlike the standard 12v alternator that comes with the engine, the Integrel system can create up to 7 kW of 48v power - 
enabling a large capacity lithium bank to be fully charged in a couple of hours.

So I contacted Integrel Solutions and over many conversations we arrived at a setup that would be suitable for the boat and our needs:

* 2 Integrel E-Drive generators (one for each engine), $32,004
* 4 MG LiFePO 25v/7200Wh batteries (connected in pairs for 50v), $21,832
* MG Lynx Smart Battery Management System (BMS), $1,184
* Victron Multiplus II 48/220v 10 kw invertor, $4,589
* 3 Orion DC-DC Convertors 48/12-360 W, $843
* 3 Ergon Frigomar 7 kBTU/h 48v air con units , $16,542
* 1 Ergon Frigomar 16 kBTUh 48v air con (for saloon), $6,488
* 2 Seawater Pumps for the Frigomar, $3,738

Another $22,114 for shipping and installation.  So the total was not cheap: $87,220.

The installation was done by Pochan in La Rochelle.  I was worried that there be some confusion with Pochan and the FP workers doing
jobs at the same time, but everyone knows everyone, and there wasn't any issues in this regard.

The Integrel generators are setup to charge the 48v bank and they basically work as advertised, delivery up to 5000 watts each
to the batteries.  Compared with the approximately 400 W output we get from the standard engine alternators.  Here the
Lithiums paired with the 48v bus really pay off as the generators can supply the charge and the batteries accept it.

With the Integrel system we basically had 3 more or less independent electrical grids:

* 12v: 4 150 Ah AGM batteries.  Supports lights, navigation, watermaker, winch, windless, frig and freezer
* 48v: 4 7200 Wh LiFePo batteries.  Supports Air con and 10 kw Multiplus Invertor
* 220v: shore power and/or Multiplus Invertor.  Supports wall sockets, water heater, oven, stove, dishwasher, laundry

Seems complicated, but there is a rational.  12v is the historic standard on boats and most 12v equipment is most popular and
cheapest.  For low wattage devices, 12v is plenty (though for the windless it would be nice to have a 48v supply).

48v enables more current to be supplied with a given wire size.  So something as power hungry as th Frigomar air con units, a 12v 
supply would be impractical, but 48v works fine.  Since the Multiplus only needs to step up from 48v to 220v, it can support a much
higher output wattage than a 12/220v invertor could.

Finally, 220v is useful for all those domestic systems that were designed for household use.  Sourcing a 48v Espresso maker might be
a challenge, but it's easy enough to pick up a regular one at the shop and plug it in.  We did have to make the decision whether to go
with the European standard 220v or the US standard 110v.  We chose 220 which was compatible with appliances we bought in the EU, but
if we take the boat back to the US, most appliances we buy in the US wouldn't work (in addition to voltage being different, the frequency is different as well, so electric motors would run at the wrong speed).  We'll face that issue when we come to it, but for now 220 v is working fine (fortunately laptop charges and such are happy at either voltage).

Sometime it can be useful to share power from the Lithium bank to the AGM bank (say the AGMs are low, but you have plenty of juice in the 48v
bank).  For this purpose there are three Orion 360 W DC-to-DC convertors that can transfer a 48v input to a 12v output.  THese will
transfer energy until the AGMs hit a preset voltage limit (indicating they are sufficiently charged).

The components are setup as follows:

Strarboard engine bay
---------------------

* Integrel generator
* MG BMS
* 4 MG LiFePo batteries
* Multiplus II 48/220 10kW invertor

Port engine bay
---------------

* Integrel generator
* 4 AGM batteries
* Multiplus 12/220 2kW invertor/charger (used to charge AGMs from shore power)
* 3 Orion 360 W DC-to-DC convertors
* Victron Cerbo GX monitoring system


With the installation of the 48v Lithium batteries we had a bit of an issue with solar setup.  From the
factory, the integrated solar panels connect to five MPPT units (stored in a rather inaccessible plywood box 
placed in the transom lazarette).  The MPPT units in turn supply power to the AGM bank.  I thought this was 
inefficient as we wouldn't be able to supply any of our 220v power needs using solar (The lithium batteries could solely
be charged by the Integrels or shore power).  And it wasn't just a matter of connecting the MPPTs to the 48v bus as
the particular models we had didn't have a 48v battery setting.  After much back and forth with Pochan, we had them
install two new MPPT units (48v capable), so about half our solar charged the 48v bank, and the other half charged the 12v
AGMs.  Since the integrated solar produced much less output than I had anticipated, we would have been fine leaving as it was
(i.e. it's unlikely we'd have maxed out our 12v needs and wasted the extra solar power).  Eventually (2026) we installed two fixed
panels on a stern arch and another one on the helm roof and that finally got us to a point where we rarely needed to use the Integrels 
(but is still nice to know they are there if we have a stretch of cloudy days).

One last point, is that I've found the support we've gotten from the Integrel team very good.  They are always fast to respond to any
support issue I have, and have visited the boat three time to check the system, install software updates, and revised hardware.

{{< figure src="new_horizon_electrical_schematic.jpg" alt="map" caption="New Horizon electrical schematic" >}}