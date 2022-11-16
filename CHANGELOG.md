# Changelog

<!--next-version-placeholder-->

## v1.74.1 (2022-11-16)
### Fix
* Building via PEP 517 ([#166](https://github.com/Bluetooth-Devices/dbus-fast/issues/166)) ([`6694fda`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6694fda49f966814ebc900a52812b4c5e4ff1980))

## v1.74.0 (2022-11-14)
### Feature
* Improve cdef types for marshaller ([#164](https://github.com/Bluetooth-Devices/dbus-fast/issues/164)) ([`9fb4440`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9fb4440b805fa5bf432fa1b23d9b1fac1de31b96))

## v1.73.1 (2022-11-14)
### Fix
* Allow non-string objects to be marshalled by write_string ([#163](https://github.com/Bluetooth-Devices/dbus-fast/issues/163)) ([`46f1d6b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/46f1d6bbc09860185db04c7985b9fd7c23e7a1bf))

## v1.73.0 (2022-11-11)
### Feature
* Reduce latency to process messages ([#161](https://github.com/Bluetooth-Devices/dbus-fast/issues/161)) ([`113f0c9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/113f0c9a325d538592555ae89e1df1ea29398aa9))

## v1.72.0 (2022-11-04)
### Feature
* Add optimized reader for GetManagedObjects ([#152](https://github.com/Bluetooth-Devices/dbus-fast/issues/152)) ([`7ed453f`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7ed453f31a654f8cc9b99eb17f872370f4b06a4e))

## v1.71.0 (2022-11-04)
### Feature
* Small speed up to _unpack_variants ([#148](https://github.com/Bluetooth-Devices/dbus-fast/issues/148)) ([`ef7acdc`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ef7acdcbe59123bfa3b17d5dafc9f8235ac0f360))

## v1.70.0 (2022-11-04)
### Feature
* Use cimports for message marshalling ([#149](https://github.com/Bluetooth-Devices/dbus-fast/issues/149)) ([`ef7d9d4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/ef7d9d440775cf0ddcb6b3bc6115b3884be35792))

## v1.69.0 (2022-11-04)
### Feature
* Refactor message_reader to avoid python wrappers ([#147](https://github.com/Bluetooth-Devices/dbus-fast/issues/147)) ([`b81de45`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b81de4553fc1414476ff8a1c2b73db7b1a497841))

## v1.68.0 (2022-11-04)
### Feature
* Use cimports for unmarshaller Variant and Message ([#146](https://github.com/Bluetooth-Devices/dbus-fast/issues/146)) ([`6418ed4`](https://github.com/Bluetooth-Devices/dbus-fast/commit/6418ed4bb69a835768596f66ab5b514ea48b82cc))

## v1.67.0 (2022-11-03)
### Feature
* Optimize unmarshaller by dropping exception that was only used internally ([#145](https://github.com/Bluetooth-Devices/dbus-fast/issues/145)) ([`79d52a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/79d52a50bd9651fa489e81935bda04d53285b2c1))

## v1.66.0 (2022-11-03)
### Feature
* Speed up creating Variant objects ([#144](https://github.com/Bluetooth-Devices/dbus-fast/issues/144)) ([`2ff84e3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2ff84e3ac56f4348c8276515ac398fcbda8a0657))

## v1.65.0 (2022-11-03)
### Feature
* Add cython def for unmarshaller read_sock for fd passing ([#143](https://github.com/Bluetooth-Devices/dbus-fast/issues/143)) ([`f438c36`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f438c369bd86956f50fb839ec4a0a8069de7d018))

## v1.64.0 (2022-11-03)
### Feature
* Speed up marshalling headers ([#142](https://github.com/Bluetooth-Devices/dbus-fast/issues/142)) ([`7d6fb63`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7d6fb63dc011404955fc1219924cd2c6f6634ccd))

## v1.63.0 (2022-11-03)
### Feature
* Speed up marshall align ([#137](https://github.com/Bluetooth-Devices/dbus-fast/issues/137)) ([`d7d301c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d7d301c773beb312be752accf7018a3dacecde02))
* Speed up marshall write_string and write_variant ([#138](https://github.com/Bluetooth-Devices/dbus-fast/issues/138)) ([`71cf524`](https://github.com/Bluetooth-Devices/dbus-fast/commit/71cf52430bd3ece01083309c5f0f5d934dca3d59))

## v1.62.0 (2022-11-03)
### Feature
* Speed up marshaller by pre-packing bools ([#139](https://github.com/Bluetooth-Devices/dbus-fast/issues/139)) ([`c10a241`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c10a241dc5e889fd58323789dc4af45ec1e5616a))

## v1.61.1 (2022-11-01)
### Fix
* Re-release due to pypi not seeing the new version ([#134](https://github.com/Bluetooth-Devices/dbus-fast/issues/134)) ([`2f21ee8`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2f21ee8b8d52975624c19b6593a96976fa19047b))

## v1.61.0 (2022-11-01)
### Feature
* Add support and workarounds for cpython3.11 ([#31](https://github.com/Bluetooth-Devices/dbus-fast/issues/31)) ([`b53a467`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b53a4675d78f8e4e37be322ebda3eeec80f15723))

## v1.60.0 (2022-10-31)
### Feature
* Speed up auth phase ([#131](https://github.com/Bluetooth-Devices/dbus-fast/issues/131)) ([`3eef636`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3eef6368268c2d46db3b31bf907959da36dbf2a4))

## v1.59.2 (2022-10-31)
### Fix
* Correctly fallback to pure python when cython is missing ([#130](https://github.com/Bluetooth-Devices/dbus-fast/issues/130)) ([`8ab1f9d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8ab1f9d0b380293294a0f847664e0c459061c2d9))

## v1.59.1 (2022-10-29)
### Fix
* Pass return value to SendReply.__exit__ ([#127](https://github.com/Bluetooth-Devices/dbus-fast/issues/127)) ([`f8c67ed`](https://github.com/Bluetooth-Devices/dbus-fast/commit/f8c67ed00fa8fe58a85b6ba73b5fa5974f802004))

## v1.59.0 (2022-10-29)
### Feature
* Speed up decoding headers by avoiding unicode checks ([#125](https://github.com/Bluetooth-Devices/dbus-fast/issues/125)) ([`6121781`](https://github.com/Bluetooth-Devices/dbus-fast/commit/61217819fbbe073007a44db69328008941d6bb4c))

## v1.58.0 (2022-10-29)
### Feature
* Add optimized parser for properties changed messages with service data ([#124](https://github.com/Bluetooth-Devices/dbus-fast/issues/124)) ([`c8a9452`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c8a945210ae3ea8d25e4547f70b25d61b778ffe1))

## v1.57.0 (2022-10-29)
### Feature
* Add optimized parser for InterfacesRemoved ([#123](https://github.com/Bluetooth-Devices/dbus-fast/issues/123)) ([`09822a5`](https://github.com/Bluetooth-Devices/dbus-fast/commit/09822a59ffad07b8dcb6d216d98e6dccbe338b06))

## v1.56.0 (2022-10-29)
### Feature
* Optimize for interfaces added messages ([#122](https://github.com/Bluetooth-Devices/dbus-fast/issues/122)) ([`c05a27a`](https://github.com/Bluetooth-Devices/dbus-fast/commit/c05a27aef9395eb688385109c4ff7204d5103dda))

## v1.55.0 (2022-10-29)
### Feature
* Add optimized reader for uint16 ([#121](https://github.com/Bluetooth-Devices/dbus-fast/issues/121)) ([`52881d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/52881d9054e35ae3d727c4adafd7e0958b1c99af))

## v1.54.0 (2022-10-28)
### Feature
* Speed up unmarshaller with common signature trees ([#120](https://github.com/Bluetooth-Devices/dbus-fast/issues/120)) ([`5b32072`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5b32072934a7269ffc7186aaaed77a0eb6872cd9))

## v1.53.0 (2022-10-28)
### Feature
* Add additional pxd defs for message ([#118](https://github.com/Bluetooth-Devices/dbus-fast/issues/118)) ([`3eb123b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3eb123b0366ed143d395e0609540c580398cd896))

## v1.52.0 (2022-10-28)
### Feature
* Small speed up to unpack_variants ([#117](https://github.com/Bluetooth-Devices/dbus-fast/issues/117)) ([`3c164a9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/3c164a9291b9fb6e75aed0fc5aab1dfc7b79c376))

## v1.51.0 (2022-10-27)
### Feature
* Inline cast uint32 and int16 to speed up unmarshall ([#115](https://github.com/Bluetooth-Devices/dbus-fast/issues/115)) ([`24dd9d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/24dd9d9742e8c779b9c8aa751ba8b2815b61b15b))

## v1.50.0 (2022-10-27)
### Feature
* Speed up unmarshall ([#114](https://github.com/Bluetooth-Devices/dbus-fast/issues/114)) ([`e1836b2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e1836b2034ca4bfbb004027f98b42c68f6c6edce))

## v1.49.0 (2022-10-26)
### Feature
* Speed up unmarshaller ([#113](https://github.com/Bluetooth-Devices/dbus-fast/issues/113)) ([`8f7f982`](https://github.com/Bluetooth-Devices/dbus-fast/commit/8f7f982a75fe9c998e5a983090e361ba52e2e6a3))

## v1.48.0 (2022-10-20)
### Feature
* Add typing to auth module ([#110](https://github.com/Bluetooth-Devices/dbus-fast/issues/110)) ([`e07e281`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e07e281ded44f9ded3002c34803f802146a9e3c9))

## v1.47.0 (2022-10-19)
### Feature
* Speed up unmarshaller ([#109](https://github.com/Bluetooth-Devices/dbus-fast/issues/109)) ([`2443cf9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2443cf99909af02db040caeeded7024a020c50a5))

## v1.46.0 (2022-10-19)
### Feature
* Speed up marshaller and add typing ([#108](https://github.com/Bluetooth-Devices/dbus-fast/issues/108)) ([`e8f568c`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e8f568c074965bf7955f29cd89cf14f1b8dd5643))

## v1.45.0 (2022-10-13)
### Feature
* Optimize signature readers for most common messages ([#107](https://github.com/Bluetooth-Devices/dbus-fast/issues/107)) ([`d5fb4d9`](https://github.com/Bluetooth-Devices/dbus-fast/commit/d5fb4d9c8bf17c51762ea961d745c5db7d8d8a22))

## v1.44.0 (2022-10-12)
### Feature
* Speed up unpack_variants ([#105](https://github.com/Bluetooth-Devices/dbus-fast/issues/105)) ([`a4fdda2`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a4fdda271f7a96e267826ffa3f268ec02078ba73))

## v1.43.0 (2022-10-12)
### Feature
* Improve aio message reader performance ([#104](https://github.com/Bluetooth-Devices/dbus-fast/issues/104)) ([`9fa697d`](https://github.com/Bluetooth-Devices/dbus-fast/commit/9fa697da65d449b7402aa7f2f26762b0d2e175c6))

## v1.42.0 (2022-10-12)
### Feature
* Complete some more missing typing ([#103](https://github.com/Bluetooth-Devices/dbus-fast/issues/103)) ([`5787032`](https://github.com/Bluetooth-Devices/dbus-fast/commit/5787032af7cae1ffffd1561390cdb02053776345))

## v1.41.0 (2022-10-11)
### Feature
* Add more typing to unmarshaller ([#102](https://github.com/Bluetooth-Devices/dbus-fast/issues/102)) ([`e7048fa`](https://github.com/Bluetooth-Devices/dbus-fast/commit/e7048fa38b63ea45e819930a51ca5744f86da73f))

## v1.40.0 (2022-10-10)
### Feature
* Speed up unmarshaller ([#101](https://github.com/Bluetooth-Devices/dbus-fast/issues/101)) ([`a6a248b`](https://github.com/Bluetooth-Devices/dbus-fast/commit/a6a248b3b1dbbb06784f700b49a7fe92b30cc7b5))

## v1.39.0 (2022-10-10)
### Feature
* Add additional typing ([#100](https://github.com/Bluetooth-Devices/dbus-fast/issues/100)) ([`cde1893`](https://github.com/Bluetooth-Devices/dbus-fast/commit/cde1893dca1872d8b482a145337ee3bbf47c35b4))

## v1.38.0 (2022-10-09)
### Feature
* Optimize for reading a{sv} messages and headers ([#98](https://github.com/Bluetooth-Devices/dbus-fast/issues/98)) ([`4648d29`](https://github.com/Bluetooth-Devices/dbus-fast/commit/4648d29df4b616f49c06ca9fcbfbc27717d97135))

## v1.37.0 (2022-10-09)
### Feature
* Speed up empty array unmarshall ([#96](https://github.com/Bluetooth-Devices/dbus-fast/issues/96)) ([`2c6ee99`](https://github.com/Bluetooth-Devices/dbus-fast/commit/2c6ee99b73dcfb2e2d45d2610a3fa10a4ff2136a))

## v1.36.0 (2022-10-09)
### Feature
* Add cdef to unpack_variants ([#95](https://github.com/Bluetooth-Devices/dbus-fast/issues/95)) ([`dbf42c3`](https://github.com/Bluetooth-Devices/dbus-fast/commit/dbf42c370784236ff31e9324968f02a5efb58586))

## v1.35.0 (2022-10-09)
### Feature
* Add unpack variants benchmark ([#94](https://github.com/Bluetooth-Devices/dbus-fast/issues/94)) ([`eb966fd`](https://github.com/Bluetooth-Devices/dbus-fast/commit/eb966fd7cf3a3f05879c29f7eb98727dd117c317))

## v1.34.0 (2022-10-09)
### Feature
* Add additional typing ([#93](https://github.com/Bluetooth-Devices/dbus-fast/issues/93)) ([`7326bdf`](https://github.com/Bluetooth-Devices/dbus-fast/commit/7326bdf097310eafa21364dd46f6ebb72baa1a3d))

## v1.33.0 (2022-10-09)
### Feature
* Improve performance of unmarshalling headers ([#88](https://github.com/Bluetooth-Devices/dbus-fast/issues/88)) ([`b6d4069`](https://github.com/Bluetooth-Devices/dbus-fast/commit/b6d40691fd11ff8d4e46a57fd8cc97a9b6806089))

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
