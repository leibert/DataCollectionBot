# Data Collection Bot
##Bot to get Weather and MBTA bus times for other puposes

Python script that is called every few minutes by a cron job to retrieve up-to-date bus times, MBTA delay alerts, and weather conditions and forecasts.
Retrieved info is written to a text file that other devices can view at their leisure on the internal network, minimizing the number of API calls made.

Info is used by both the [LED Info Sign](https://github.com/leibert/LEDsign) and the [Bus-o-tron](https://github.com/leibert/ESPNode/tree/master/deployed/Busotron/ESPNode)

