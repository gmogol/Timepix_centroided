# Timepix_centroided

This is a sister repository of my Timepix repostiory. In this case another external code (written in C++) is taking care of centroiding. The main goal here is to syncronize TDC2 (phosphor screen trigger) with TDC1 (laser trigger) data streams. TDC1 and centroided data takes the standard csv format, whose header looks as follows:
* ``#TrigId, #TrigTime, #Col, #Row, #ToA, #ToT[arb], #ToTtotal[arb], #Trig-ToA[arb], #Centroid, #cent_X, #cent_Y ,#centStdev_X, #centStdev_Y, #centStdev_ToA``

Of particular importance to us is TrigId and TrigTime (TDC1). TrigId is the events recorded for a given laser pulse. In particular if we have a 3 electron event then we would have 3 lines with the same TrigId. We use TrigId to identify and reject many electron events so all events with the same TridId is rejected. 

We synchronize TDC1 with TDC2 by iterating over TDC2 list until the difference between TDC2-TDC1 is minimal. The even is rejected if this difference is negative as the laser trigger always precedes phosphor screen trigger. Furthermore, if this difference is too high it's again rejected as an unphysical event. All physical events occur within roughly 4us and certainly less than 5us (default thresholding parameter).
