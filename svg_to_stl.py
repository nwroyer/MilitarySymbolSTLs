import os
import subprocess
import re

def svg_to_stl(unit_name:str):
	cwd = os.path.dirname(__file__)
	print(unit_name)

	svg_file = re.sub(r'\s+', '_', f'{unit_name}.svg')

	if re.match(r'\d+', item):
		cmd = ['military-symbol', f'"{item}"', '-o', svg_file, '-b', '-c', 'ff4400']
	else:
		cmd = ['military-symbol', '-n', f'"{item}"', '-o', svg_file, '-b', '-c', 'ff4400']
		
	print(' '.join(cmd))
	subprocess.run(' '.join(cmd), shell=True)

	# Convert strokes to paths using Inkscape

	cmd = [
		'inkscape', 
		'--actions="select-all:all;object-stroke-to-path"',
		f'--export-filename="{svg_file}"',
		svg_file
	]

	print(' '.join(cmd))
	subprocess.run(' '.join(cmd), shell=True)

	# Convert to STL with Blender script
	cmd = ['blender', '--background', '--factory-startup', '--python', os.path.join(cwd, 'svg_to_stl_blender.py'), '--', svg_file]

	print(' '.join(cmd))
	subprocess.run(cmd)

	# Remove intermediate SVG file
	subprocess.run(['rm', svg_file])
	
if __name__ == '__main__':
	cwd = os.path.dirname(__file__)
	items = []
	with open(os.path.join(cwd, 'items.txt'), 'r') as in_file:
		items = [line.strip() for line in in_file]

	for item in items:
		svg_to_stl(unit_name=item)