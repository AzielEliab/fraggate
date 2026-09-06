# FragGate — iPhone & Android

On-device reminder that FragGate is the door: list / describe / call / verify.
Not a second kernel. Offline scaffold. No analytics. Dark matte / gold.

Application id: `com.azieeliab.fraggate`

## Open in Android Studio / Xcode

The `android/` and `ios/` folders here are skeleton READMEs because
this tree was written without the Flutter SDK on PATH.

```bash
cd mobile
flutter create --org com.azieeliab --project-name fraggate .
flutter pub get
flutter run
```

Then open `android/` in Android Studio, or `ios/Runner.xcworkspace` in
Xcode.

## Honest scope

This phone app does not replace the Worker UI or the catalog MCP.
Agent path stays `POST https://aziel-runtime.vibelock.workers.dev/mcp`
and `/v1/fraggate/*`.

## Desktop package (counted download)

# → https://fraggate-download-tracker.vibelock.workers.dev/ ←

GitHub: https://github.com/AzielEliab/fraggate

**Forks are welcome and always allowed.**
