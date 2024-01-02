[![HACS Default](https://img.shields.io/badge/HACS-Default-blue.svg)](https://github.com/hacs/default)
[![GitHub release](https://img.shields.io/github/release/myTselection/pixometer.svg)](https://github.com/myTselection/pixometer/releases)
![GitHub repo size](https://img.shields.io/github/repo-size/myTselection/pixometer.svg)

[![GitHub issues](https://img.shields.io/github/issues/myTselection/pixometer.svg)](https://github.com/myTselection/pixometer/issues)
[![GitHub last commit](https://img.shields.io/github/last-commit/myTselection/pixometer.svg)](https://github.com/myTselection/pixometer/commits/master)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/myTselection/pixometer.svg)](https://github.com/myTselection/pixometer/graphs/commit-activity)

# Pixometer Home Assistant integration
[Pixometer](https://pixometer.io/info/) Home Assistant custom component. With Pixometer, a mobile app and scan solutions is available for intuitive and efficient meter reading registration. This custom component has been built from the ground up to bring your Pixometer scaned engery meter usage details into Home Assistant to help you towards a better follow up on your usage information. This integration is built against the public website provided by Pixolus Pixometer.

This integration is in no way affiliated with Pixolus or Pixmeter. **Please don't report issues with this integration to Pixometer, they will not be able to support you.**

Some discussion on this topic can be found within the community discussion [Home Assistant Forum](https://community.home-assistant.io/t/pixometer-integration/285608)

Pixometer account creation: https://pixometer.io/portal/#/login 

Pixometer app [Android](https://play.google.com/store/apps/details?id=com.pixolus.pixometer) / [iPhone](https://apps.apple.com/app/apple-store/id934332635)
<p align="right"><img src="https://raw.githubusercontent.com/myTselection/pixometer/master/logo.png" width="128"/></p>
<!-- <p align="center"><img src="https://github.com/myTselection/pixometer/blob/main/Gauge%20Card%20Configuration.png"/></p> -->


## Installation
- Make sure you have a free [Pixometer account](https://pixometer.io/portal/#/login) created
- [HACS](https://hacs.xyz/): HACS > Integration > search for Pixometer and install
  - [![Open your Home Assistant instance and open the repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg?style=flat-square)](https://my.home-assistant.io/redirect/hacs_repository/?owner=myTselection&repository=pixometer&category=integration)
- Restart Home Assistant
- Add 'Pixometer' integration via HA Settings > 'Devices and Services' > 'Integrations'
- Provide Pixometer username and password
- A sensor Pixometer should become available per meter with last reading as state and further details as attribute.

## Status
Still some optimisations are planned, see [Issues](https://github.com/myTselection/pixometer/issues) section in GitHub.

## Example usage:
For each meter, a sensor will be created in HA.
Myself, I still have a fuel oil installation which has no meter similar to gas meter. I only have a televar indicating the percentage of oil currently available in the tank.

At a regular interval I do keep track of this percentage of oil within a Pixometer meter reading. 

Next, with a template sensor, I convert the percentage of tank content into a total number of kWh used so far:
- Within a HA variable `input_number.mazout_bijvullingen`, I keep track of the total number of liters orderd to fill the oil tank. 
- But since not all of this total orderd oil is already consumed, I substract the number of liters still available in the tank to know the total number of used liter of fuel. 
- The number of liters left in the tank is calculated based on the percentage left in the tank and the max capacity of the tank (5000l)
- The number of liters used is then converted from liters into kWh by multipling by 10.641.

Configuration as a template sensor in `configuration.yaml`

```
sensor: 
  - platform: template
    sensors:
      mazout_pixometer:
        value_template: "{{ ((states.input_number.mazout_bijvullingen.state|float - 5000) + (5000 * (100 - states('sensor.pixometer_mazout_televar_thuis')|float)/100)) * 10.641}}"
        device_class: gas
        unit_of_measurement: kWh
```
