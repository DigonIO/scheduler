#!/bin/bash
pkgname=python-scheduler
pkgver=0.6.3
pkgrel=1
pkgdec='A simple in-process python scheduler'
arch=('any')
license=('LGPL3')
depends=('python' 'python-typeguard')
makedepends=('python-setuptools')
checkdepends=('mypy' 'python-pytest-cov' 'python-typing_extensions')
source=("https://gitlab.com/DigonIO/scheduler/-/archive/$pkgver/scheduler-$pkgver.tar.gz")

b2sums=('aa6cd40d36a0d1a9de7e22971266626b4207cb24da8059b9340a27fd5e09ddcb706f90f60db5d6da2399f9bfd84b5e8c5d19d15089f3879c589f97cfc775255a')


build() {
  cd scheduler-$pkgver
  python setup.py build
}

check() {
  cd scheduler-$pkgver
  PYTHONPATH="$PWD/build/lib" MYPYPATH="$PWD/build/lib" pytest --cov=scheduler/ tests/
  PYTHONPATH="$PWD/build/lib" MYPYPATH="$PWD/build/lib" pytest --doctest-modules doc/pages/*/*.rst
}

package() {
  cd scheduler-$pkgver
  python setup.py install --root="$pkgdir" --optimize=1

  install -Dm644 LICENSE -t "$pkgdir"/usr/share/licenses/$pkgname/
}