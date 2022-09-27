# Changelog

<!--next-version-placeholder-->

## v1.17.0 (2022-09-27)
### Feature
* Improve unmarshaller performance ([#43](https://github.com/Bluetooth-Devices/dbus-fast/issues/43)) ([`c4b4a03`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c4b4a038f8822b6be7b062184b8092b6249878bc))

## v1.16.0 (2022-09-27)
### Feature
* Add benchmark for bluez properties messages ([#42](https://github.com/Bluetooth-Devices/dbus-fast/issues/42)) ([`076c5df`](https://github.com/Bluetooth-Devices/dbus-fast/commit/076c5df825221901d1565e45f8662d7d9009ffe9))

## v1.15.3 (2022-09-27)
### Fix
* Improve typing on proxy_object ([#41](https://github.com/Bluetooth-Devices/dbus-fast/issues/41)) ([`ac955b5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ac955b50ea2921b114f6a89c2e1d3fbf34698deb))

## v1.15.2 (2022-09-27)
### Fix
* More typing fixes ([#40](https://github.com/Bluetooth-Devices/dbus-fast/issues/40)) ([`a6b9581`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a6b9581d6228bf2cb4b93531677acc959e2d4dd1))

## v1.15.1 (2022-09-26)
### Fix
* Loosen async-timeout pin to 3.0.0 ([#39](https://github.com/Bluetooth-Devices/dbus-fast/issues/39)) ([`93b9a0a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/93b9a0a6ca91adb6c64d9316bd977a359c3be007))

## v1.15.0 (2022-09-26)
### Feature
* Use async_timeout instead of asyncio.wait_for ([#38](https://github.com/Bluetooth-Devices/dbus-fast/issues/38)) ([`cb31780`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cb317802d654bbff7b09233b4cce6188179f1d45))

## v1.14.0 (2022-09-25)
### Feature
* Speed up unmarshaller read_array ([#37](https://github.com/Bluetooth-Devices/dbus-fast/issues/37)) ([`18ea18d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/18ea18d7d224764b7f529cb6238ac524f0bd8318))

## v1.13.0 (2022-09-24)
### Feature
* Improve unmarshall performance ([#35](https://github.com/Bluetooth-Devices/dbus-fast/issues/35)) ([`db436b7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/db436b7a10a38438a9a7f50349ddb41b112c3312))

## v1.12.0 (2022-09-24)
### Feature
* Speed up unmarshall ([#34](https://github.com/Bluetooth-Devices/dbus-fast/issues/34)) ([`5a1e26f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5a1e26f4302ed1ff3a4582e6710e2c5f99cb4a32))

## v1.11.0 (2022-09-24)
### Feature
* Speed up marshalling ([#32](https://github.com/Bluetooth-Devices/dbus-fast/issues/32)) ([`afcf5fe`](https://github.com/Bluetooth-Devices/dbus-fast/commit/afcf5fe1d9c1c4a632edc60b5d48d8af32d13159))

## v1.10.0 (2022-09-24)
### Feature
* Improve writer performance with a deque ([#30](https://github.com/Bluetooth-Devices/dbus-fast/issues/30)) ([`09af56e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/09af56e14397d9bdf183239c30683c76b7e34801))

## v1.9.0 (2022-09-24)
### Feature
* Improve asyncio write performance ([#29](https://github.com/Bluetooth-Devices/dbus-fast/issues/29)) ([`016e71e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/016e71ef6d7de4d9295f3ca170d7352ae233d74a))

## v1.8.0 (2022-09-24)
### Feature
* Small speed ups to unmarshall message creation ([#27](https://github.com/Bluetooth-Devices/dbus-fast/issues/27)) ([`0bce72a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0bce72a76a6af0d7b3c731e08393652747e6c53a))

## v1.7.0 (2022-09-21)
### Feature
* Handle kwargs in signal callback ([#26](https://github.com/Bluetooth-Devices/dbus-fast/issues/26)) ([`2e8076b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2e8076b14abf297b83eb2c81b0cacff405845d95))

## v1.6.0 (2022-09-20)
### Feature
* Add unpack variants option ([#20](https://github.com/Bluetooth-Devices/dbus-fast/issues/20)) ([`cfad28b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cfad28bd2ba8dccf4c3a591461bb666871e4cbba))

### Fix
* Disconnect connected buses at end of tests ([#25](https://github.com/Bluetooth-Devices/dbus-fast/issues/25)) ([`e438890`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e43889091bf7b21f6ffd27544d74cc1d57db22d2))

## v1.5.1 (2022-09-20)
### Fix
* Marshall boolean correctly ([#23](https://github.com/Bluetooth-Devices/dbus-fast/issues/23)) ([`ca2a3c1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ca2a3c1aa86f1f0b6372929f099e8594dab2697f))

## v1.5.0 (2022-09-19)
### Feature
* Allow varargs callback for signals ([#22](https://github.com/Bluetooth-Devices/dbus-fast/issues/22)) ([`a3379c7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a3379c74ad8f8da1eb15b6cd941d9bea6867b5f9))

## v1.4.0 (2022-09-10)
### Feature
* Improve unmarshalling performance ([#18](https://github.com/Bluetooth-Devices/dbus-fast/issues/18)) ([`4362b93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4362b93fc84406adfa026b6573bc076327c71c5b))

## v1.3.0 (2022-09-09)
### Feature
* Improve callback performance ([#16](https://github.com/Bluetooth-Devices/dbus-fast/issues/16)) ([`aee3da9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/aee3da9f20c36cf6379d1e69e63f33a88592f6fd))

## v1.2.0 (2022-09-09)
### Feature
* Improve Marshaller performance ([#15](https://github.com/Bluetooth-Devices/dbus-fast/issues/15)) ([`a9e8866`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a9e8866c2a6a97227ff5f001cae5e2196260379c))

## v1.1.9 (2022-09-09)
### Fix
* Readme ([#13](https://github.com/Bluetooth-Devices/dbus-fast/issues/13)) ([`6bc87e0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6bc87e0f0717d4a4382e4bb36d064e22ff131751))

## v1.1.8 (2022-09-09)
### Fix
* Ensure the underlying socket is closed on disconnect ([#12](https://github.com/Bluetooth-Devices/dbus-fast/issues/12)) ([`6770a65`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6770a656bdddf6e090ebb6858bd046e4365ea32e))

## v1.1.7 (2022-09-09)
### Fix
* Copyrights in docs ([#10](https://github.com/Bluetooth-Devices/dbus-fast/issues/10)) ([`a97701e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a97701ec12e4049884af33abbde2b208c4e351d4))

## v1.1.6 (2022-09-09)
### Fix
* Docs deps not needed for production ([#9](https://github.com/Bluetooth-Devices/dbus-fast/issues/9)) ([`01f8ce7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/01f8ce77b945554f27723755caab550b6f246cb4))

## v1.1.5 (2022-09-09)
### Fix
* Readme ([#8](https://github.com/Bluetooth-Devices/dbus-fast/issues/8)) ([`7396b5f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7396b5f475e4b9299cf96930153a01425bb5bd3b))

## v1.1.4 (2022-09-09)
### Fix
* More rename ([#7](https://github.com/Bluetooth-Devices/dbus-fast/issues/7)) ([`116d5c6`](https://github.com/Bluetooth-Devices/dbus-fast/commit/116d5c6feb863deff95f811d79199b09c79552f9))

## v1.1.3 (2022-09-09)
### Fix
* Docs ([#6](https://github.com/Bluetooth-Devices/dbus-fast/issues/6)) ([`ee473c0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ee473c05c5ff1ecc91f0c0167987e970eebf4c75))

## v1.1.2 (2022-09-09)
### Fix
* Readme ([#5](https://github.com/Bluetooth-Devices/dbus-fast/issues/5)) ([`f628e87`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f628e87a1b859966dac03143a7a14422ef0d79a1))
* Docs ([#4](https://github.com/Bluetooth-Devices/dbus-fast/issues/4)) ([`ba8e5f1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ba8e5f127f2a4e20254a8d652165c348d0b9884f))

## v1.1.1 (2022-09-09)
### Fix
* Docs lang ([#3](https://github.com/Bluetooth-Devices/dbus-fast/issues/3)) ([`538db98`](https://github.com/Bluetooth-Devices/dbus-fast/commit/538db98a3b7246e5d3ace256ac3b86c3dae5b63e))

## v1.1.0 (2022-09-09)
### Feature
* Speed up unmarshaller ([#1](https://github.com/Bluetooth-Devices/dbus-fast/issues/1)) ([`eca1d31`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eca1d317818d2b938ec3ed3172b1be76a44a93a4))
