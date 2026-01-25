# FAQ

## How often is data refreshed?

Data is refreshed every 6 hours.

## Do you support older versions of the integration?

Due to time constraints, I will only ever support the latest version of the integration. If you have an issue with an older version of the integration, my initial answer will always be to update to the latest version. This might be different to what HACS is reporting if you are not on the minimum supported Home Assistant version (which is highlighted in each release's changelog). 

## How do I know when there's an update available?

If you've installed via HACS, and you are on version 2 or above, then updates will be surfaced in the normal update location within Home Assistant. If you are on a version below 2, then you can keep an eye on `sensor.hacs` to see the number of pending updates. This could be used with an automation or highlighted on your dashboard. This will include any HACS integration update, not just this one.

If you've installed the integration manually, then you should keep an eye on the [GitHub releases](https://github.com/BottlecapDave/HomeAssistant-Smol/releases). You could even subscribe to the [RSS feed](https://github.com/BottlecapDave/HomeAssistant-Smol/releases.atom).

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.
