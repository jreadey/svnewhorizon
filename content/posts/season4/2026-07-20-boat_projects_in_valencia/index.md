+++
date = '2026-07-23T15:20:03+02:00'
draft = false 
title = 'Boat projects in Valencia'
description = "Boat projects in Valencia"
tags = ["projects", "mediterranean", "spain", "valencia"]
categories = ["Travel"]
showToc = true
TocOpen = false

[cover]
    image = "IMG_3487.jpg" 
    alt = "Solar panel install"
    caption = "Looking to see how solar panels could be fitted"
    relative = true # Tells PaperMod to look inside the current post folder
+++

{{< map lat="39.4234" lng="-0.3201" zoom="13" title="Valencia Mar" caption="Valencia Mar">}}

We arrived in Valencia again to drop off our guests (who planned to visit more cities on the Spainish mainland), 
and to have some work down on our boat.  We stayed at the Valencia Mar marina (where we had stayed last time we visited).
The marina is nice enough, but it's quite hard to get to town from there.  In the end we were fairly busy dealing with the 
projects, so didn't have much time for sightseeing anyway (other than a visit to the Valencia Aquarium which we didn't have a 
chance to visit last time).

Last season we had trashed our code zero and ended up leaving it with North Sails at loft in Valencia Mar to be repaired over the
off season.  On the way to Valencia, we had ANOTHER sail disaster when the luff tore out of the genoa.  Luckily that was not as big 
a job as with the code zero and the North Sails show was able to fix it with just a week of work.

The other project we wanted to get done while in Valencia is installation of additional solar panels.  We bought the boat 
with the integrated solar option (flexible panels installed on the coach roof).  Fountain Pajot claims a max of 1700 W, but 
in practice we rarely saw more than 800 W.  With three refrigerators, electric oven and hob, washer/dryer, and dishwasher, our
electrical consumption greatly outpaced the solar production.  Our lithium batteries could store 27 kWh of power, and with the integrel 
generators we could charge them at 6 kW, but if we had any time between using the engine (sailing or at anchorage), after 3 or 4 days
our batteries would be getting low.  I estimated another 1000 W of solar power would basically be enough for us to keep up with our energy
needs.

I contacted Joaquin at [Mediterranean Yacht Solutions](https://www.medyachtssol.com/) who is based in Valencia about which option would be best
for us.   I had an idea to just use the same kind of panels we have now (Solbian flex panel) as we had locations on the coach roof and helm roof where 
these panels could be custom fitted (and would match our existing setup cosmetically).   After getting a quote from Solbian, we dropped that idea 
as they were crazy expense ($12/W vs $3/W).  After many back and forth emails we decided on installing two
 [FuturaSun FU590M SILK Nova Duetto 590W](https://www.futurasun.com/wp-content/uploads/2024/05/FuturaSun_144_565-590W_Silk-Nova-Duetto_EN.pdf) panels on a stern mounted arch.

In addition to the MG Lithium batteries, we have 4 AGM batteries with 12 kW capacity.  The AGM batteries power our 12 v systems (friges, lights, windless, etc.)
while the Lithium batteries power the 48v grid (basically our air con units and the Victron invertor).  MYS suggested changing the AGMs for Lithiums, but
besides the expense this would require a additional starter battery for the port engine (since Lithiums don't produce the right kind power needed for engine starting).  
In the end we stayed with the AGM for the house loads.  Since the Orion chargers ensure the AGMs never get to low, they should have a few more years of life left.  Then
we can decide to move to Lithium or just get a new set of AGMs.

Anyway, to enable charging the AGM bank from the Lithium bank we 
have 3 400 W Victron DC-DC units that can be turned on or off via a switch in the cabin.  This need a fair bit of attention to turn off or on appropriately.  If they
are left off, the only way they can be charged is with the 2 MPPT solar controllers, or the standard port engine alternator (which typically won't be enough to
keep up with daily usage).  If left on, the batteries will always be 100% charged, but then there will be no ability to utilize the solar panels that are connected with
the 12 V bank.  To avoid this management burden it turns out we need the latest model Orion convertors ("dump" convertor to "smart" convertor).  Physically they look
the same, but the smart convertor can enable transfer when the AGM batteries are at a certain voltage level.  I set them (using the Victron App via Bluetooth) to transfer
power only when the AGM voltage is less than 12.8 V.  This way we can just leave the cabin switch on, and the units will reserve capacity so that solar can charge the
batteries but also step in if the battery voltage falls too low.

Once we arrived in Valencia Mar, Joaquin and his gang came on board and started taking measurements for fabricating the stern arch.  Their work shop is right at the
marina which was convenient as there was a lot of coming and going between the workshop and the boat.  Originally MYS wanted to have three supports (left, center, and right),
but Rong was not too happy about that as the center support would block the view and make it harder to get into the dinghy.  On the other hand, MYS was afraid
with two supports there would be too much flex at sea. In the end we decided on two supports with an additional horizontal bracing bar.  Another dicsussion was whether there
should be 2 or 4 panels.  For boats like ours a common arrangement is to have the panels start just after the traveler (overlapping the coach roof) and extending out for 
enough that 4 panels can be supported.  In our case, that would block the existing soft panels we have, so we went with two panels on the arch.

MYS wanted to the panels to send power to our AGM batteries.  I preferred it go to the Lithium bank (as we could always transfer power from 48 to 12 v, but not vice versa).
The concern was that to provide enough voltage, the two panels would need to be connected in series with one MPPT controller.  This would make them more sensitive to losing
power due to shading.  In practice the panels are paced so far to the aft that shadowing hasn't been a problem.   

Around this time, I noticed that the helm roof was just the right size to mount a third panel.  MYS was able to make some mounting brackets and run the wires down to a second MPPT
that went to the AGM bank.  I was hoping that this panel (plus our two MPPTs from the original soft panels) would be enough to meet our 12v consumption (and it turned out to be the case,
the AGM panels go to float by early afternoon most days).  So now we had an extra 1800 W of solar, double our rated capacity and more than that in practice (since the soft panels are much less efficient).  After some time with this setup it's worked out very well.  We hardly ever use the Integrel generator now and even at the dock don't bother to connect the shore power.

There were two other small jobs we had MYS do... First we had them install a galvanic isolator.  This avoid problems with stray current when connected to shore power (which ironically we
rarely use now).  The second was installation of a temperature controlled engine blower for the the starboard engine room.  The factory blower only runs when the engine is on, but 
when sailing in hot weather (>95 F), the engine bay can get so hot even without the engine running, that the BMS will disallow charging once the temperature hits 112 F which we saw
for the first time in the Med during August.  It turned out the supplier only shipped one blower (we wanted one for intake and one for outtake), so MYS had the second blower shipped to Mallorca where I would install it myself (not a hard job).

So quite a bit of planning, work and money for these updates, but it's really improved our ability to be off-grid with less worry.  Our only concern is that this is the summer
we finally started to use our air con units (it never got hot enough in the North Sea or Baltic we felt we needed).  Even though these are energy efficient 48v units, they 
still use quite a bit of power (500-2000W per unit).  So while our solar is sufficient for our use without AC, with AC we don't make nearly enough to keep all 4 units running.  The best we can do is to cool the saloon during the day and our cabin during the night if we want to avoid using the engine.  Well you can't have everything and except for the hottest times in the
summer, we don't usually run the AC anyway.



{{< figure src="IMG_4751.jpg" alt="map" caption="More Victron hardware!" >}}

{{< figure src="IMG_4755.jpg" alt="map" caption="Farewell paella dinner for Nai-Rong and Elaine's last day with us" >}}

{{< figure src="IMG_4756.jpg" alt="map" caption="Our Paella chef" >}}

{{< figure src="IMG_4823.jpg" alt="map" caption="Finally the frame is ready" >}}


{{< figure src="IMG_4826.jpg" alt="map" caption="The panels are installed" >}}


{{< figure src="IMG_4827.jpg" alt="map" caption="Just the wiring to hook up now" >}}

{{< figure src="IMG_4829.jpg" alt="map" caption="A third panel was placed on the helm roof" >}}

{{< figure src="IMG_4831.jpg" alt="map" caption="The marina mis-read the meter and tried to charge us for enough water to fill a couple of olympic size swimming pools!" >}}
