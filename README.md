[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

# Pixometer (Beta)
[Pixometer](https://pixometer.io/info/) Home Assistant custom component. With Pixometer, a mobile app and scan solutions is available for intuitive and efficient meter reading registration.
discussion [Home Assistant Forum](https://community.home-assistant.io/t/pixometer-integration/285608)

Pixometer account creation: https://pixometer.io/portal/#/login 
<p align="right"><img src="https://github.com/myTselection/pixometer/blob/main/logo.png" width="128"/></p>
<!-- <p align="center"><img src="https://github.com/myTselection/pixometer/blob/main/Gauge%20Card%20Configuration.png"/></p> -->


## Installation
- Make sure you have a free [Pixometer account](https://pixometer.io/portal/#/login) created
- [HACS](https://hacs.xyz/): add url https://github.com/myTselection/pixometer as custom repository (HACS > Integration > option: Custom Repositories)
- Restart Home Assistant
- Add 'Pixometer' integration via HA Settings > 'Devices and Services' > 'Integrations'
- Provide Pixometer username and password
- A sensor Pixometer should become available per meter with last reading as state and further details as attribute.

## TODO
- Add logo
- Add 'reload' option
- Register repo as standard HACS repo

## Example usage:
### TODO
```

```
<p align="center"><img src="https://github.com/myTselection/pixometer/blob/main/example.png"/></p>
