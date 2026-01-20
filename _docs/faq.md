# FAQ

## How often is data refreshed?

Data is refreshed every 6 hours.

## Do you support older versions of the integration?

Due to time constraints, I will only ever support the latest version of the integration. If you have an issue with an older version of the integration, my initial answer will always be to update to the latest version. This might be different to what HACS is reporting if you are not on the minimum supported Home Assistant version (which is highlighted in each release's changelog). 

## How do I know when there's an update available?

If you've installed via HACS, and you are on version 2 or above, then updates will be surfaced in the normal update location within Home Assistant. If you are on a version below 2, then you can keep an eye on `sensor.hacs` to see the number of pending updates. This could be used with an automation or highlighted on your dashboard. This will include any HACS integration update, not just this one.

If you've installed the integration manually, then you should keep an eye on the [GitHub releases](https://github.com/BottlecapDave/HomeAssistant-Smol/releases). You could even subscribe to the [RSS feed](https://github.com/BottlecapDave/HomeAssistant-Smol/releases.atom).

## There's a beta release of the integration that I would like to take part in, how do I do this?

If you install the integration manually, it's just a case of getting the source of the [beta release](https://github.com/BottlecapDave/HomeAssistant-Smol/releases), replacing the old installation with the new one and restarting Home Assistant.

If you install the integration via HACS, then you will need to

* Go to [HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=homeassistant-smol&category=integration), click on the three dots and then click redownload

![Redownload screen in HACS](./assets/beta-hacs-redownload.png)

* If you are on version 2 or above, then click on `Need a different version?` and select the `Release` box and then select your target `pre-release` version

![Beta toggle in HACS](./assets/beta-hacs-pre-release.png)

If you are on a version below 2, then toggle on `Show beta versions` and select the target beta. Once selected, click `Download`.

![Beta toggle in HACS](./assets/beta-hacs-beta-toggle.png)

* Once downloaded, you'll need to restart Home Assistant for the new version to take effect.

## How do I increase the logs for the integration?

If you are having issues, it would be helpful to include Home Assistant logs as part of any raised issue. This can be done by following the [instructions](https://www.home-assistant.io/docs/configuration/troubleshooting/#enabling-debug-logging) outlined by Home Assistant.

You should run these logs for about a day and then include the contents in the issue. Please be sure to remove any personal identifiable information from the logs before including them.

## I've been asked for diagnostic data in a bug request, how do I obtain this?

If you've been asked for diagnostic information, don't worry we won't ask for anything sensitive. To obtain this information

1. Navigate to the [Smol integration](https://my.home-assistant.io/redirect/integration/?domain=smol)
2. Click the three dots next to your account configuration
3. Click on "Download diagnostics"
4. Take the contents of the downloads json file and paste into the bug report. Remember to surround the contents with ``` both at the start and end.
