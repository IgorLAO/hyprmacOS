#!/usr/bin/env python3
"""Calcula a refração condicional SpecV1 Dock Tahoe 26.6.1 (25G76).

Evidência SQLite: tahoe26:re-auto:dock-dimensional-conversion.
Implementação própria da conversão observada; não determina dimensões runtime,
perfil do filtro ou unidades do renderizador e não aplica presets ao compositor.
"""
import argparse
import json
import math


def dock_refraction(minimum=None, largest=None, *, dimensions_absent=False, pixel_length=1.0,
                    w27_bit5=None, w24_bit9=None):
    """Valores da receita para entradas explícitas de Environment.dimensions."""
    for name, value in [('minimum', minimum), ('largest', largest), ('pixel_length', pixel_length)]:
        if value is not None and (not math.isfinite(value) or value < 0):
            raise ValueError(f'{name} deve ser finito e não negativo')
    if pixel_length <= 0:
        raise ValueError('pixel_length deve ser positivo')
    if dimensions_absent and (minimum is not None or largest is not None):
        raise ValueError('dimensões ausentes não podem conter distâncias')
    if (w27_bit5 is None) != (w24_bit9 is None):
        raise ValueError('os dois bits de estado devem ser informados juntos')
    if any(value is not None and not isinstance(value, bool) for value in (w27_bit5, w24_bit9)):
        raise ValueError('bits de estado devem ser booleanos')
    inner = 48.0 if dimensions_absent or minimum is None else minimum
    outer = 48.0 if dimensions_absent else (inner if largest is None else largest)
    # DesignLibrary 25G76 0x240958bf8..c44: sem nome semântico dos bits.
    normalized_inner_height = 0.0 if w27_bit5 is True and w24_bit9 is False else .127
    return {
        'innerHeight': min(max(normalized_inner_height * inner, 0.0), 20.0),
        'innerAmount': max(-.42 * inner, -60.0),
        'outerHeight': .13 * outer,
        'outerAmount': .42 * outer,
        'outerDistances': [-1.0, pixel_length - 1.0],
        'outerOpacity': .20000000298023224,  # Float .2, como no binário
    }


def filter_inputs(refraction):
    """Chaves CAFilter confirmadas em BackgroundFilter.refraction (offset224)."""
    return {
        'inputInnerRefractionHeight': refraction['innerHeight'],
        'inputInnerRefractionAmount': refraction['innerAmount'],
        'inputOuterRefractionHeight': refraction['outerHeight'],
        'inputOuterRefractionAmount': refraction['outerAmount'],
        'inputRefractionDistance0': refraction['outerDistances'][0],
        'inputRefractionDistance1': refraction['outerDistances'][1],
        'inputRefractionOpacity': refraction['outerOpacity'],
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--minimum', type=float, help='minimumDistance explícita; omissão representa nil')
    p.add_argument('--largest', type=float, help='minimumDistanceOfLargestArea explícita; omissão representa nil')
    p.add_argument('--dimensions-absent', action='store_true', help='Environment.dimensions=nil')
    p.add_argument('--pixel-length', type=float, required=True, help='pixelLength explícito do ambiente')
    for flag in ('w27-bit5', 'w24-bit9'):
        p.add_argument('--' + flag, choices=('0', '1'),
                       help='bit bruto observado no builder Dock 25G76; informe os dois')
    args = p.parse_args()
    if args.minimum is None and args.largest is None and not args.dimensions_absent:
        p.error('informe uma distância ou --dimensions-absent; não inferir o ambiente do Dock')
    try:
        values = dock_refraction(args.minimum, args.largest,
                                 dimensions_absent=args.dimensions_absent, pixel_length=args.pixel_length,
                                 w27_bit5=None if args.w27_bit5 is None else args.w27_bit5 == '1',
                                 w24_bit9=None if args.w24_bit9 is None else args.w24_bit9 == '1')
    except ValueError as error:
        p.error(str(error))
    print(json.dumps({
        'version': '26.6.1', 'build': '25G76',
        'evidence': 'tahoe26:re-auto:dock-dimensional-conversion',
        'inputs': vars(args), 'refraction': values,
        'filter_type': 'glassBackground', 'filter_inputs': filter_inputs(values),
        'limitations': ['Entradas fornecidas pelo usuário; não são dimensões medidas do Dock Apple.',
                        'O sentido dos bits w27.bit5 e w24.bit9 e seus valores em runtime são desconhecidos; sem flags a ramificação é presumida inativa.',
                        'Unidades/perfil do filtro e associação ao shader hyprglass ainda não verificados.'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
