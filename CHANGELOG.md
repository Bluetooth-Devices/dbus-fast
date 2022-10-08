# Changelog

<!--next-version-placeholder-->

## v1.32.0 (2022-10-08)
### Feature
* Speed up marshalling arrays ([#87](https://github.com/Bluetooth-Devices/dbus-fast/issues/87)) ([`f554345`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f554345b3640524300fbe406f4ac25dbf61a2274))

## v1.31.0 (2022-10-08)
### Feature
* Speed up marshalling variants ([#86](https://github.com/Bluetooth-Devices/dbus-fast/issues/86)) ([`7847e26`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7847e26e6e6cfe172437544d7709dc0c87a65402))

## v1.30.0 (2022-10-08)
### Feature
* Speed up aligning data during marshall ([#85](https://github.com/Bluetooth-Devices/dbus-fast/issues/85)) ([`07e6886`](https://github.com/Bluetooth-Devices/dbus-fast/commit/07e68862d93cd5dc470ad2a3ae6f8eaf12808271))

## v1.29.1 (2022-10-07)
### Fix
* Remove unused unmarshaller code ([#83](https://github.com/Bluetooth-Devices/dbus-fast/issues/83)) ([`3613ff8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3613ff846b8bb66000c65c778bb06596cd643b22))

## v1.29.0 (2022-10-07)
### Feature
* Unpack header names as message kwargs ([#82](https://github.com/Bluetooth-Devices/dbus-fast/issues/82)) ([`7398a3f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7398a3fc4726fa20b34840967a6c3777eef12f52))

## v1.28.1 (2022-10-07)
### Fix
* Disconnect race in tests ([#79](https://github.com/Bluetooth-Devices/dbus-fast/issues/79)) ([`f2bb106`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f2bb10680a5d4e363ff8e7762fef25ec75ef8b14))

## v1.28.0 (2022-10-07)
### Feature
* Speed up unmarshalling int16 types ([#81](https://github.com/Bluetooth-Devices/dbus-fast/issues/81)) ([`18213c0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/18213c0a00f162cbf74fa7fc0bbcf12c1109c347))

## v1.27.0 (2022-10-07)
### Feature
* Cythonize headers in unmarshaller ([#80](https://github.com/Bluetooth-Devices/dbus-fast/issues/80)) ([`ae96be7`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ae96be70f5e960d3feb726b7c769dff26b41c428))

## v1.26.0 (2022-10-06)
### Feature
* Add cython defs for Variant class ([#74](https://github.com/Bluetooth-Devices/dbus-fast/issues/74)) ([`cd08f06`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cd08f063cc352c65d2330cbe09ca72a367c58806))

### Fix
* Incorrect pxd typing for for _marshall ([#75](https://github.com/Bluetooth-Devices/dbus-fast/issues/75)) ([`cf1f012`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cf1f0129baaac48d6a4804e8c6a0af5bc7ef8d16))

## v1.25.0 (2022-10-05)
### Feature
* Add cython extension for messages ([#73](https://github.com/Bluetooth-Devices/dbus-fast/issues/73)) ([`8676f12`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8676f12a7e040d7c3f20584739a74ad1074a4717))

## v1.24.0 (2022-10-04)
### Feature
* Add cython extension for signature ([#72](https://github.com/Bluetooth-Devices/dbus-fast/issues/72)) ([`0ad8801`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0ad8801215093cdbf0f62fce5b953d9b01e9d524))

## v1.23.0 (2022-10-04)
### Feature
* Speed up unmarshall performance ([#71](https://github.com/Bluetooth-Devices/dbus-fast/issues/71)) ([`f38e08f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f38e08fa7cc8d41e896663ab0f163aa37a472abe))

## v1.22.0 (2022-10-03)
### Feature
* Speed up message bus matching ([#70](https://github.com/Bluetooth-Devices/dbus-fast/issues/70)) ([`cccfea3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cccfea30b9ec5417eecef5093ee02f7b7a254c45))

## v1.21.17 (2022-10-02)
### Fix
* Install python-semantic-release in wheel workflow ([#68](https://github.com/Bluetooth-Devices/dbus-fast/issues/68)) ([`cca0d6e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cca0d6e98a5934fee83ccafbd2ed47cf60a3ce99))

## v1.21.16 (2022-10-02)
### Fix
* Ensure we can get the latest version in the wheels build process ([#67](https://github.com/Bluetooth-Devices/dbus-fast/issues/67)) ([`ecd5a70`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ecd5a7036945ccdd79e3049a7f2904709544af51))

## v1.21.15 (2022-10-02)
### Fix
* Checkout main for wheels ([#66](https://github.com/Bluetooth-Devices/dbus-fast/issues/66)) ([`3051a93`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3051a9322cc711cee24583dedf25cee31a31c3b3))

## v1.21.14 (2022-10-02)
### Fix
* Use semantic-release to find the latest tag for wheels ([#65](https://github.com/Bluetooth-Devices/dbus-fast/issues/65)) ([`b76eb97`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b76eb97188c204996d049d326b4d21c74bc3f325))

## v1.21.13 (2022-10-02)
### Fix
* Build wheels from the sha saved after release ([#64](https://github.com/Bluetooth-Devices/dbus-fast/issues/64)) ([`faee181`](https://github.com/Bluetooth-Devices/dbus-fast/commit/faee18172bb7bc72ade8a54f2a8bd0fae5e35018))

## v1.21.12 (2022-10-02)
### Fix
* Switch to on create instead of push ([#63](https://github.com/Bluetooth-Devices/dbus-fast/issues/63)) ([`af0ed88`](https://github.com/Bluetooth-Devices/dbus-fast/commit/af0ed889985425b33fbbe35e8c8a4d0427643367))

## v1.21.11 (2022-10-02)
### Fix
* Accept any tag to build wheels ([#62](https://github.com/Bluetooth-Devices/dbus-fast/issues/62)) ([`60fca54`](https://github.com/Bluetooth-Devices/dbus-fast/commit/60fca54d2a4da67e3211b9e3f421787154234041))

## v1.21.10 (2022-10-02)
### Fix
* Github action tag matching ([#61](https://github.com/Bluetooth-Devices/dbus-fast/issues/61)) ([`b95d0b8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b95d0b8ce63e03c972fef72354cd67c2062bea94))

## v1.21.9 (2022-10-02)
### Fix
* Build wheels on tag instead ([#60](https://github.com/Bluetooth-Devices/dbus-fast/issues/60)) ([`6166896`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6166896c49a1358c951057fcc73d4b91ac92e08b))

## v1.21.8 (2022-10-02)
### Fix
* Publish wheels when release happens ([#59](https://github.com/Bluetooth-Devices/dbus-fast/issues/59)) ([`45e8ac0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/45e8ac00c6473c5329b36d4f19f5eb846db19d31))

## v1.21.7 (2022-10-02)
### Fix
* Seperate wheels back out so it builds after ([#58](https://github.com/Bluetooth-Devices/dbus-fast/issues/58)) ([`c74c251`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c74c2519a12a0f9cbb8c1b12b8871df22dda047d))

## v1.21.6 (2022-10-02)
### Fix
* Language_level warning when running cythonize ([#57](https://github.com/Bluetooth-Devices/dbus-fast/issues/57)) ([`b7b441e`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b7b441eeef8bfa1dc286c78435ff9bac9d072302))

## v1.21.5 (2022-10-02)
### Fix
* Cython build of unpack ([#56](https://github.com/Bluetooth-Devices/dbus-fast/issues/56)) ([`5df01ac`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5df01ac1ba3dc0515ffa8d0b01c1d386ef726e91))

## v1.21.4 (2022-10-02)
### Fix
* Increase verbosity of wheel builds ([#55](https://github.com/Bluetooth-Devices/dbus-fast/issues/55)) ([`4779e7b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4779e7b825270268ae28b5fc1c4ddb45647c31c5))

## v1.21.3 (2022-10-02)
### Fix
* Make wheel build depend on release success ([#54](https://github.com/Bluetooth-Devices/dbus-fast/issues/54)) ([`49d98d0`](https://github.com/Bluetooth-Devices/dbus-fast/commit/49d98d01c2a3736adcc5d088fdd447c45b9503de))

## v1.21.2 (2022-10-02)
### Fix
* Additional tweaks to publishing wheels ([#53](https://github.com/Bluetooth-Devices/dbus-fast/issues/53)) ([`05b9453`](https://github.com/Bluetooth-Devices/dbus-fast/commit/05b945317380ad3d50b2f9d9114a61a2c57d99f0))

## v1.21.1 (2022-10-02)
### Fix
* Wheel builds on released ([#52](https://github.com/Bluetooth-Devices/dbus-fast/issues/52)) ([`6259fb2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6259fb299722688ca19a41a61a7a783e9abdca8c))

## v1.21.0 (2022-10-02)
### Feature
* Cythonize unpack_variants ([#51](https://github.com/Bluetooth-Devices/dbus-fast/issues/51)) ([`1587211`](https://github.com/Bluetooth-Devices/dbus-fast/commit/158721123fc56675f04b9081ef4107590a8c2b17))

## v1.20.0 (2022-10-02)
### Feature
* Add additional cython types to the unmarshaller ([#45](https://github.com/Bluetooth-Devices/dbus-fast/issues/45)) ([`0f279a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/0f279a5ea9cd440fdbdd7dbafc1a48b1cc3577d7))

### Fix
* Add missing closes to tests ([#49](https://github.com/Bluetooth-Devices/dbus-fast/issues/49)) ([`d2ce4a1`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d2ce4a18462b5e304bc75983be3fffa3c426affc))

## v1.19.0 (2022-10-02)
### Feature
* Add additional cython types to marshaller ([#48](https://github.com/Bluetooth-Devices/dbus-fast/issues/48)) ([`ddba96a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ddba96a73107644e31af591d8b726472a7deb85b))

## v1.18.0 (2022-10-01)
### Feature
* Add optional cython extension ([#44](https://github.com/Bluetooth-Devices/dbus-fast/issues/44)) ([`b737574`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b737574cf04f5c6b6f881fbdce2663119a6dc404))

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
