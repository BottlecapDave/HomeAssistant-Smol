# Home Assistant Smol

![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.smol.total) [![](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bottlecapdave)
- [Home Assistant Smol](#home-assistant-smol)
  - [Features](#features)
  - [How to install](#how-to-install)
    - [HACS](#hacs)
    - [Manual](#manual)
  - [How to setup](#how-to-setup)
  - [Docs](#docs)
  - [FAQ](#faq)
  - [Sponsorship](#sponsorship)

Custom component built from the ground up to bring your Smol details into Home Assistant to help you towards a more energy efficient (and or cheaper) home. This integration is built against the API provided by Smol UK and has not been tested for any other countries. 

This integration is in no way affiliated with Smol.

If you find this useful and are planning on moving to Smol, why not use my [referral link](http://smol.refr.cc/default/u/davidk8)?

## Features

Below are the main features of the integration



## How to install

There are multiple ways of installing the integration. Once you've installed the integration, you'll need to [setup your account](#how-to-setup) before you can use the integration.

### HACS

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

This integration can be installed directly via HACS. To install:

* [Add the repository](https://my.home-assistant.io/redirect/hacs_repository/?owner=BottlecapDave&repository=homeassistant-smol&category=integration) to your HACS installation
* Click `Download`

### Manual

You should take the latest [published release](https://github.com/BottlecapDave/HomeAssistant-Smol/releases). The current state of `develop` will be in flux and therefore possibly subject to change.

To install, place the contents of `custom_components` into the `<config directory>/custom_components` folder of your Home Assistant installation. Once installed, don't forget to restart your home assistant instance for the integration to be picked up.

## How to setup

Please follow the [setup guide](https://bottlecapdave.github.io/HomeAssistant-Smol/setup/account) to setup your initial account. This guide details the configuration, along with the sensors that will be available to you.

## Docs

To get full use of the integration, please visit the [docs](https://bottlecapdave.github.io/HomeAssistant-Smol/).

## FAQ

Before raising anything, please read through the [faq](https://bottlecapdave.github.io/HomeAssistant-Smol/faq). If you have questions, then you can raise a [discussion](https://github.com/BottlecapDave/HomeAssistant-Smol/discussions). If you have found a bug or have a feature request please [raise it](https://github.com/BottlecapDave/HomeAssistant-Smol/issues) using the appropriate report template.

## Sponsorship

If you are enjoying the integration, why not use my [referral link](http://smol.refr.cc/default/u/davidk8) if you're not already a part of Smol, or if possible, make a one off or monthly [GitHub sponsorship](https://github.com/sponsors/bottlecapdave).
