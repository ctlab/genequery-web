module.exports = function (grunt) {
  "use strict";

  require("load-grunt-tasks")(grunt);

  grunt.initConfig({

    nodeModulesDir: 'node_modules',

    staticCssDir: 'static/css',
    staticJsDir: 'static/js',
    distJsDir: 'static/js/dist',
    libJsDir: 'static/js/dist/lib',
    staticFontsDir: 'static/fonts',

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
      prod: {
        src: '<%= staticJsDir %>/searcher/searcher.js',
        dest: '<%= distJsDir %>/searcher.js'
      },
      dev: {
        src: '<%= staticJsDir %>/searcher/searcher.js',
        dest: '<%= distJsDir %>/searcher.min.js'
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
          '<%= distJsDir %>/searcher.es5.js': '<%= distJsDir %>/searcher.js'
        }
      }
    },

    uglify: {
      main: {
        files: {
          '<%= distJsDir %>/searcher.min.js': ['<%= distJsDir %>/searcher.es5.js']
        }
      }
    },

    watch: {
      files: [
        // Include
        '<%= staticJsDir %>/**/*.js',
        '<%= staticJsDir %>/**/*.jsx',

        // Exclude
        '!<%= distJsDir %>/**/*',
        '!<%= staticJsDir %>/searcher/ui/**/*.js'
      ],
      tasks: ['dev']
    }
  });

  grunt.registerTask('dev', ['react', 'browserify:dev', 'watch']);
  grunt.registerTask('build', ['copy', 'react', 'browserify:prod', 'babel', 'uglify']);

};