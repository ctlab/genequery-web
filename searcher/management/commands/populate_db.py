from optparse import make_option
import tarfile
from searcher.models import ModuleDescription, IdMap, GQModule

__author__ = 'smolcoder'

from django.core.management.base import BaseCommand, CommandError
import json


class Command(BaseCommand):
    args = '<path to tar.gz archive with initial data>'

    required_files = ['geo_data.hs.json', 'geo_data.mm.json',
                      'id_map.mm', 'id_map.hs',
                      'module_genes.hs.data', 'module_genes.mm.data']

    help = "Populates DB with initial data: modules, genes, id map, etc.\n" \
           "Following files are supposed to be in the archive: " + ', '.join(required_files)

    outer_dir_name = 'initial_data'

    store_options = ['geo', 'id_maps', 'modules']

    option_list = BaseCommand.option_list + (
        make_option('-s', '--store',
                    action='append',
                    dest='store',
                    type='string',
                    help='Specify data being stored: id_maps, modules or geo'),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Specify path to initial_data.tar.gz archive.")
        try:
            tar = tarfile.open(args[0])
        except tarfile.TarError, e:
            raise CommandError(e)
        files = tar.getnames()
        self.validate_files(files)
        store_data = options['store'] or self.store_options
        if 'geo' in store_data:
            self.populate_module_descriptions(self.get_file(tar, 'geo_data.mm.json'))
            self.populate_module_descriptions(self.get_file(tar, 'geo_data.hs.json'))
        if 'id_maps' in store_data:
            self.populate_id_map('mm', self.get_file(tar, 'id_map.mm'))
            self.populate_id_map('hs', self.get_file(tar, 'id_map.hs'))
        if 'modules' in store_data:
            self.populate_modules_with_genes('mm', self.get_file(tar, 'module_genes.mm.data'))
            self.populate_modules_with_genes('hs', self.get_file(tar, 'module_genes.hs.data'))

    def get_file(self, tar, name):
        return tar.extractfile(self.outer_dir_name + '/' + name)

    def populate_modules_with_genes(self, species, module_genes_file):
        existing_modules = set(GQModule.objects.values_list('species', 'module'))
        self.stdout.write("Reading data from {}...".format(module_genes_file.name))
        modules = [tuple(line[:-1].split('\t')) for line in module_genes_file.readlines()]
        entities = []
        for module, genes in modules:
            if (species, module) in existing_modules:
                continue
            entities.append(GQModule(species=species, module=module, entrez_ids=map(int, genes.split())))
        self.stdout.write("{} was red where {} new entities. Saving...".format(len(modules), len(entities)))
        GQModule.objects.bulk_create(entities)
        self.stdout.write("Saved.")

    def populate_module_descriptions(self, geo_data_file):
        existing_series = set(ModuleDescription.objects.values_list('series', flat=True))
        self.stdout.write("Loading GEO data from {}...".format(geo_data_file.name))
        geo_data = json.load(geo_data_file)
        entries = []
        for series, data in geo_data.items():
            if series in existing_series:
                continue
            organisms = data['organisms'] or data['organism']
            entries.append(ModuleDescription(
                series=series,
                status=data['status'],
                title=data['title'],
                organisms=organisms,
                overall_design=data['overall design'],
                summary=data['summary'],
                experiment_type=data['experiment type']))
        self.stdout.write("{} new entities from {} was red.".format(len(entries), len(geo_data)))
        ModuleDescription.objects.bulk_create(entries)
        self.stdout.write('Saved.')

    def populate_id_map(self, species, id_map_file):
        existing_maps = set(IdMap.objects.values_list('species', 'entrez_id', 'refseq_id', 'symbol_id'))
        self.stdout.write("Reading {}...".format(id_map_file.name))
        maps = [line[:-1].split('\t') for line in id_map_file.readlines()]
        maps = set([(species, x[0], x[1], x[2]) for x in maps])
        self.stdout.write("Saving {} maps for {} was red where there are {} new maps. Saving...".format(
            len(maps), species, len(maps - existing_maps)))
        maps = maps - existing_maps
        entries = []
        for _, e, r, s in maps:
            s = s.upper()
            if r == '-':
                r = None
            if s == '-':
                s = None
            entries.append(IdMap(species=species, entrez_id=int(e), refseq_id=r, symbol_id=s))
        IdMap.objects.bulk_create(entries)
        self.stdout.write("Saved.")

    def validate_files(self, files):
        for f in self.required_files:
            full_name = self.outer_dir_name + '/' + f
            if full_name not in files:
                raise CommandError("File {} is absent in {}. See help.".format(full_name, files))
