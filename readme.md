# QR Code Generator

QR Code Generator is an open source library for encoding strings and numerics into a QR code.

It is currently in development. It will be available as an API which will take in strings/numerics and return an object of bits representing the QR code.


Eh, this was meant to be an alternative to services charging a fee for logo placement. All you really need to do though, is use the qrgen library for python (or anything else for that matter), create a QR code with a redundancy level H, and you can modify up to approx 30% of the code without losing information. Logo placement is therefore just done by placing it somewhere over non timing, position, or alignment sections so that it doesn't obstruct more than up to approx 30% of data.


### Done:

* Data analysis (if you consider this a step)
* Data encoding

### To do:

* Error correction coding
* Structuring final message
* Module placement
* Data masking
* Format and version information

Algorithms from [thonky](http://thonky.com/qr-code-tutorial/introduction)
