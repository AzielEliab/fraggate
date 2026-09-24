import 'package:flutter/material.dart';

/// Paper and charcoal surfaces, gold focus. System light/dark.
const Color kMatteBlack = Color(0xFF12110F);
const Color kSurface = Color(0xFF1C1B18);
const Color kGold = Color(0xFFC9A227);
const Color kGoldDim = Color(0xFF8A7219);
const Color kIvory = Color(0xFFF3EFE6);
const Color kPaper = Color(0xFFF6F4EF);
const Color kInk = Color(0xFF1C1915);

ThemeData buildAppTheme() => buildDarkTheme();

ThemeData buildLightTheme() {
  const scheme = ColorScheme.light(
    primary: kInk,
    onPrimary: kPaper,
    secondary: kGold,
    onSecondary: kInk,
    surface: Color(0xFFFFFDF8),
    onSurface: kInk,
    error: Color(0xFF7A2E2E),
    onError: kPaper,
  );
  return _theme(scheme, kPaper);
}

ThemeData buildDarkTheme() {
  const scheme = ColorScheme.dark(
    primary: kGold,
    onPrimary: kMatteBlack,
    secondary: kGoldDim,
    onSecondary: kIvory,
    surface: kSurface,
    onSurface: kIvory,
    error: Color(0xFFF0B4B4),
    onError: kMatteBlack,
  );
  return _theme(scheme, kMatteBlack);
}

ThemeData _theme(ColorScheme scheme, Color scaffold) {
  const goldSide = BorderSide(color: kGold, width: 2);
  final buttonSide = MaterialStateProperty.resolveWith<BorderSide?>((states) {
    if (states.contains(MaterialState.focused)) return goldSide;
    return null;
  });
  final overlay = MaterialStateProperty.resolveWith<Color?>((states) {
    if (states.contains(MaterialState.focused)) return const Color(0x55C9A227);
    return null;
  });
  final buttonStyle = ButtonStyle(side: buttonSide, overlayColor: overlay);
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: scaffold,
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: scaffold,
      foregroundColor: scheme.onSurface,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: scheme.outlineVariant),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(style: buttonStyle),
    textButtonTheme: TextButtonThemeData(style: buttonStyle),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: scheme.surface,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
  );
}
