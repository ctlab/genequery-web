module.exports = function (grunt) {
  "use strict";

  require("load-grunt-tasks")(grunt);

  grunt.initConfig({

    nodeModulesDir: 'node_modules',

    staticCssDir: 'css',
    staticJsDir: 'js',
    libJsDir: 'js/lib',
    staticFontsDir: 'fonts',

    pkg: grunt.file.readJSON('package.json'),

    react: {
      build_UI: {
        options: {
          ignoreMTime: true
        },
        files: [
          {
            expand: true,
            cwd: '<%= staticJsDir %>/searcher/jsx/',
            src: ['**/*.jsx'],
            dest: '<%= staticJsDir %>/searcher/ui/',
            ext: '.js'
          }
        ]
      }
    },

    browserify: {
      searcher: {
        src: 'js/searcher/searcher.js',
        dest: 'js/searcher/searcher.build.js'
      }
    },

    copy: {
      js: {
        files: [
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/bootstrap/dist/js/',
            src: ['**'],
            dest: '<%= libJsDir %>/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/jquery/dist/',
            src: ['**'],
            dest: '<%= libJsDir %>/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/magnific-popup/dist/',
            src: ['**/*min.js'],
            dest: '<%= libJsDir %>/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/floatthead/dist/',
            src: ['**/*min.js'],
            dest: '<%= libJsDir %>/',
            filter: 'isFile'
          }
        ]
      },
      css_and_fonts: {
        files: [
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/bootstrap/dist/css/',
            src: ['**'],
            dest: '<%= staticCssDir %>/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/bootstrap/dist/fonts/',
            src: ['**'],
            dest: '<%= staticFontsDir %>/',
            filter: 'isFile'
          },
          {
            expand: true,
            cwd: '<%= nodeModulesDir %>/magnific-popup/dist/',
            src: ['*.css'],
            dest: '<%= staticCssDir %>/',
            filter: 'isFile'
          }
        ]
      }
    },

    babel: {
      options: {
        sourceMap: true,
        presets: ['es2015']
      },
      dist: {
        files: {
          '<%= staticJsDir %>/searcher/searcher.final.js': '<%= staticJsDir %>/searcher/searcher.build.js'
        }
      }
    },

    uglify: {
      main: {
        files: {
          '<%= staticJsDir %>/searcher/searcher.min.js': ['<%= staticJsDir %>/searcher/searcher.final.js']
        }
      }
    },

    watch: {
      files: [
        '<%= staticJsDir %>/**/*',
        '!<%= libJsDir %>/**/*',
        '!<%= staticJsDir %>/ui/**/*.js'
      ],
      tasks: ['default']
    }
  });

  grunt.registerTask('default', ['react', 'browserify', 'watch']);
  grunt.registerTask('build', ['copy', 'react', 'browserify', 'babel']);

};