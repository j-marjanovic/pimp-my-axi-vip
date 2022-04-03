git diff --no-index modify.txt.orig     modify.txt     > modify.patch      || true
git diff --no-index add.txt.orig        add.txt        > add.patch         || true
git diff --no-index remove.txt.orig     remove.txt     > remove.patch      || true
git diff --no-index example_pkg.sv.orig example_pkg.sv > example_pkg.patch || true
git diff --no-index example2.sv.orig    example2.sv    > example2.patch    || true
