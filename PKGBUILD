#!/bin/bash
pkgname=python-scheduler
pkgver=0.8.4
pkgrel=1
pkgdec='A simple in-process python scheduler'
arch=('any')
license=('LGPL3')
depends=('python' 'python-typeguard')
makedepends=('python-setuptools')
checkdepends=('mypy' 'python-pytest-cov' 'python-typing_extensions' 'python-pytest-asyncio')
source=("https://gitlab.com/DigonIO/scheduler/-/archive/$pkgver/scheduler-$pkgver.tar.gz")

b2sums=('923db2ae1a2fdf158627694c727dfc550466ec455451d57056476270483509756c2e029f56d86c45f1bfa8c6a20b2eecbddffdfc878ec86e11b4df80a188989f')

build() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  python setup.py build
}

check() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  py.test --cov=scheduler tests/
  py.test --doctest-modules doc/pages/*/*.rst
}

package() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  python setup.py install --root="$pkgdir" --optimize=1

  install -Dm644 LICENSE -t "$pkgdir"/usr/share/licenses/$pkgname/
}
