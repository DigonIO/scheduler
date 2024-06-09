#!/bin/bash
pkgname=python-scheduler
pkgver=0.8.7
pkgrel=1
pkgdec='A simple in-process python scheduler'
arch=('any')
license=('LGPL3')
depends=('python' 'python-typeguard')
makedepends=('python-setuptools' 'python-build' 'python-installer')
checkdepends=('mypy' 'python-pytest-cov' 'python-typing_extensions' 'python-pytest-asyncio')
source=("https://gitlab.com/DigonIO/scheduler/-/archive/$pkgver/scheduler-$pkgver.tar.gz")

b2sums=('SKIP')

build() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  python -m build --wheel
}

check() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  py.test --cov=scheduler tests/
  py.test --doctest-modules doc/pages/*/*.rst
}

package() {
  cd "$srcdir"/scheduler-"$pkgver" || exit
  python -m installer --destdir="$pkgdir" dist/*.whl

  install -vDm 644 LICENSE -t "$pkgdir"/usr/share/licenses/$pkgname/
  install -vDm 644 README.md -t "$pkgdir"/usr/share/doc/$pkgname/
}
