// REPO: antora-ui-stargate | FILE: gulp.d/tasks/lint-css.js | CONSTELLATION25

'use strict'

const stylelint = require('gulp-stylelint')
const vfs = require('vinyl-fs')

module.exports = (files) => (done) =>
  vfs
    .src(files)
    .pipe(stylelint({ reporters: [{ formatter: 'string', console: true }], failAfterError: true }))
    .on('error', done)
