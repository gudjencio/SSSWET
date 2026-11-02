# SSSWET application distribution

SSSWET is distributed through the official website and the repository's GitHub Releases.

## Mobile

The website is a Progressive Web App (PWA). On supported Android browsers, visitors can use the installation prompt or the browser menu to install SSSWET on the home screen. On iOS, open the website in Safari, choose Share, then Add to Home Screen.

An Android APK preview is also built by the application release workflow. It is currently built as a debug-signed package for preview and testing. It is not a Play Store production release and should not be treated as a stable signed upgrade channel. A production Android release requires a project-controlled signing key stored as protected repository secrets and a documented key backup/rotation policy.

## Desktop

The desktop wrapper uses Electron and packages the same public web interface. Initial packages are not code-signed or notarized, so Windows SmartScreen or macOS Gatekeeper may display a warning. Production signing and notarization require platform-specific certificates and protected secrets. Release builds target:
- Windows: NSIS installer (.exe)
- macOS: disk image (.dmg)
- Linux: AppImage

The application uses a restricted renderer configuration: context isolation and sandboxing are enabled, and Node.js integration is disabled. External HTTPS and mail links are handed to the operating system.

## Publishing

Create and push a version tag such as `v1.0.0` to trigger the release workflow. The workflow builds desktop packages on their respective operating systems, builds the Android preview APK, and attaches the resulting files to the GitHub Release.

A manual workflow run uploads build artifacts to GitHub Actions but does not publish a GitHub Release. The first public installers and Android preview package will appear in the Releases archive only after a version tag is published and the build succeeds. SHA-256 checksums are attached to each release for integrity verification.

Official downloads are linked from the SSSWET website. Do not distribute unsigned, altered or unofficial packages as official SSSWET releases.

## Shared application source

The mobile and desktop wrappers package the public `web/` interface. They do not include or grant access to unpublished research materials or private services beyond the public API configured by the website. The online platform remains available without installing an application.
