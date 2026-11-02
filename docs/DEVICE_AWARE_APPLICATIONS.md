# Device-aware applications

SSSWET presents the application path that matches the device detected by the browser.

## Routing

- **Android:** the mobile application entry points to the official Android release channel.
- **iPhone/iPad:** the interface identifies Apple mobile devices separately and presents the iPhone/iPad web-app installation path. SSSWET does not claim that a native iOS package exists until an official iOS build is published.
- **Computer:** the interface presents the official desktop release channel for Windows, macOS and Linux.

Detection is based on browser platform information and is used only to improve the installation experience. It is not used as proof of ownership, identity or eligibility.

## Localization

The device-aware application panel uses the currently selected SSSWET interface language and listens for language changes without requiring a page reload. The routing layer has dedicated translations for the maintained core application locales and uses the existing language catalogue as the source of the selected locale.

Interface text must not be silently presented as translated when a reviewed translation is unavailable. English fallback remains explicit for catalogue entries that have not yet received a maintained translation.

## Release integrity

Only published official releases are presented as downloadable application builds. A workflow or source-tree build is not described as a downloadable installer until the corresponding release asset is actually published.

This routing layer does not create or imply native Android, iOS, Windows, macOS or Linux availability by itself.
