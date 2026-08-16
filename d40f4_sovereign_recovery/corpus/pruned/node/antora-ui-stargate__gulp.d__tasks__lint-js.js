// REPO: antora-ui-stargate | FILE: gulp.d/tasks/lint-js.js | CONSTELLATION25

'use strict'

const eslint = require('gulp-eslint')
const vfs = require('vinyl-fs')

module.exports = (files) => (done) =>
  vfs
    .src(files)
    .pipe(eslint())
    .pipe(eslint.format())
    .pipe(eslint.failAfterError())
    .on('error', done)
