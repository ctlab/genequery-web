module.exports = function(grunt) {
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-browserify');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-bower-requirejs');
    grunt.loadNpmTasks('grunt-react');

    grunt.registerTask('default', ['react', 'browserify', 'watch']);
    grunt.registerTask('jsx', ['react']);
    //grunt.registerTask('bowerReq', ['bowerRequirejs']);

    grunt.initConfig({
        staticJsDir: 'js/',
        pkg: grunt.file.readJSON('package.json'),

        //uglify: {
        //    dist: {
        //        files: {
        //            '<%= staticJsDir %>/findem.min.js': ['<%= staticJsDir %>/findem.js']
        //        }
        //    }
        //},

        //bowerRequirejs: {
        //    all: {
        //        rjsConfig: '<%= staticJsDir %>/searcher/main.js',
        //        options: {
        //            exclude: [
        //                'angular',
        //                'requirejs'
        //            ]
        //        }
        //    }
        //},

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
          //build_main: {
          //  options: {
          //    ignoreMTime: true
          //  },
          //  files: {
          //    '<%= staticJsDir %>/searcher/main.js': '<%= staticJsDir %>/searcher/main.jsx'
          //  }
          //}
        },

        browserify: {
          searcher: {
            src: 'js/searcher/main.js',
            dest: 'js/searcher/main.build.js'
          }
        },

        watch: {
            files: [
                '<%= staticJsDir %>/**/*',
                '<%= staticJsDir %>/ui/**/*.js'
            ],
            tasks: ['default']
        }
    });
};