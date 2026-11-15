#!/usr/bin/env bash
# Pruebas Java de dumbtv, adaptadas de su CI MIT (b35f3ad).
set -euo pipefail
cd "$(dirname "$0")/.."
HOST_DIR=$(mktemp -d)
trap 'rm -rf "$HOST_DIR"' EXIT
mkdir -p "$HOST_DIR/main" "$HOST_DIR/config"
jar="$ANDROID_HOME/platforms/android-25/android.jar"
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/main" integrations/dumbtv/src/tv/dumbtv/home/HomeRetry.java \
  integrations/dumbtv/tests/HomeRetryTest.java
java -cp "$HOST_DIR/main" tv.dumbtv.home.HomeRetryTest
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/main" integrations/dumbtv/src/tv/dumbtv/home/OwnWindow.java \
  integrations/dumbtv/tests/OwnWindowTest.java
java -cp "$HOST_DIR/main" tv.dumbtv.home.OwnWindowTest
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/main" integrations/dumbtv/src/tv/dumbtv/home/GridGeometry.java \
  integrations/dumbtv/tests/GridGeometryTest.java
java -cp "$HOST_DIR/main" tv.dumbtv.home.GridGeometryTest
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/config" \
  integrations/dumbtv/tests/stubs/android/*/*.java integrations/dumbtv/src/tv/dumbtv/home/Config.java \
  integrations/dumbtv/tests/ConfigTest.java
java -cp "$HOST_DIR/config" tv.dumbtv.home.ConfigTest
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/main" integrations/dumbtv/src/tv/dumbtv/home/IconMatch.java \
  integrations/dumbtv/tests/IconMatchTest.java
java -cp "$HOST_DIR/main" tv.dumbtv.home.IconMatchTest
javac -d "$HOST_DIR/main" -cp "$jar" integrations/dumbtv/src/tv/dumbtv/home/FocusColor.java \
  integrations/dumbtv/src/tv/dumbtv/home/Config.java integrations/dumbtv/src/tv/dumbtv/home/Library.java \
  integrations/dumbtv/src/tv/dumbtv/home/Recent.java integrations/dumbtv/tests/FocusColorTest.java
java -cp "$HOST_DIR/main:$jar" tv.dumbtv.home.FocusColorTest
javac -d "$HOST_DIR/main" -cp "$HOST_DIR/main:$jar" integrations/dumbtv/src/tv/dumbtv/home/Recent.java \
  integrations/dumbtv/tests/RecentTest.java
java -cp "$HOST_DIR/main:$jar" tv.dumbtv.home.RecentTest
javac --release 8 -Xlint:all -Xlint:-options -Werror -d "$HOST_DIR/config" -cp "$jar:$HOST_DIR/config" \
  integrations/dumbtv/src/tv/dumbtv/home/Item.java integrations/dumbtv/src/tv/dumbtv/home/Recent.java \
  integrations/dumbtv/src/tv/dumbtv/home/Catalog.java integrations/dumbtv/tests/AppSectionsTest.java
java -cp "$HOST_DIR/config:$jar" tv.dumbtv.home.AppSectionsTest
javac -d "$HOST_DIR/main" -cp "$HOST_DIR/main:$jar" integrations/dumbtv/src/tv/dumbtv/home/Ui.java \
  integrations/dumbtv/src/tv/dumbtv/home/Meter.java integrations/dumbtv/tests/MeterTest.java
java -cp "$HOST_DIR/main:$jar" tv.dumbtv.home.MeterTest
javac -d "$HOST_DIR/main" -cp "$HOST_DIR/main:$jar" integrations/dumbtv/tests/LibraryTest.java
java -cp "$HOST_DIR/main:$jar" tv.dumbtv.home.LibraryTest
