#pragma once
#ifndef _COLORUTILS_H_
#define _COLORUTILS_H_

#include <math.h>

// https://en.wikipedia.org/wiki/Relative_luminance

float
rel_luminance(const float r, g, b)
{
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

float
rel_luminance(const vector rgb)
{
    return rel_luminance(rgb.r, rgb.g, rgb.b);
}

float
rel_luminance(const float r, g, b, a)
{
    return rel_luminance(r, g, b) * a;
}

float
rel_luminance(const vector4 rgba)
{
    return rel_luminance(rgba.r, rgba.g, rgba.b) * rgba.a;
}

vector
rgb_to_xyz(const float r, g, b)
{
    error('Not Implemented');
}

vector
rgb_to_xyz(const vector rgb)
{
    return rgb_to_xyz(rgb.r, rgb.g, rgb.b);
}

vector
xyz_to_lab(const float x, y, z)
{
    error('Not Implemented');
}

vector
xyz_to_lab(const vector xyz)
{
    error('Not Implemented');
}

vector
rgb_to_hsl(const vector rgb)
{
    return ctransform('cspace:hsl', rgb);
}

vector
rgb_to_hsl(const float r, g, b)
{
    return rgb_to_hsl(set(r, g, b));
}

vector
hsl_to_rgb(const vector hsl)
{
    return ctransform('cspace:rgb', 'cspace:hsl', hsl);
}

vector
hsl_to_rgb(const float h, s, l)
{
    return hsl_to_rgb(set(h, s, l));
}

// https://en.wikipedia.org/wiki/CIELAB_color_space

vector
rgb_to_lab(const vector rgb)
{
    return ctransform('cspace:Lab', rgb);
}

vector
rgb_to_lab(const float r, g, b)
{
    return rgb_to_lab(vector(set(r, g, b)));
}

vector
lab_to_rgb(const vector rgb)
{
    return ctransform('cspace:Lab', 'cspace:rgb', rgb);
}

vector
lab_to_rgb(const float r, g, b)
{
    return lab_to_rgb(vector(set(r, g, b)));
}

// https://en.wikipedia.org/wiki/Color_difference#CIE76

float
delta_e76(const vector lab1, lab2)
{
    return distance2(lab1, lab2);
}

// https://en.wikipedia.org/wiki/HCL_color_space

vector
lab_to_lch(const float l, a, b)
{
    float c = sqrt(a * a + b * b);
    float h = atan2(b, a);
    h += (h >= 0) * M_PI;
    return set(l, c, h);
}

vector
lab_to_lch(const vector lab)
{
    return lab_to_lch(lab.x, lab.y, lab.z);
}

vector
lch_to_lab(const float l, c, h)
{
    error('Not Implemented');
}

vector
lch_to_lab(const vector lch)
{
    return lch_to_lab(lch.x, lch.y, lch.z);
}

// Blending Methods
#define COLOR_BLEND_NORMAL 0

#define COLOR_BLEND_DARKEN 1
#define COLOR_BLEND_MULTIPLY 2
#define COLOR_BLEND_COLOR_BURN 3
#define COLOR_BLEND_LINEAR_BURN 4
#define COLOR_BLEND_DARKER_COLOR 5

#define COLOR_BLEND_LIGHTEN 6
#define COLOR_BLEND_SCREEN 7
#define COLOR_BLEND_COLOR_DODGE 8
#define COLOR_BLEND_LINEAR_DODGE 9
#define COLOR_BLEND_LIGHTER_COLOR 10

#define COLOR_BLEND_OVERLAY 11
#define COLOR_BLEND_SOFT_LIGHT 12
#define COLOR_BLEND_HARD_LIGHT 13

#define COLOR_BLEND_DIFFERENCE 14
#define COLOR_BLEND_EXCLUDE 15
#define COLOR_BLEND_SUBTRACT 16
#define COLOR_BLEND_DIVIDE 17

#define COLOR_BLEND_HUE 18
#define COLOR_BLEND_SATURATION 19
#define COLOR_BLEND_COLOR 20
#define COLOR_BLEND_LUMINOSITY 21

vector
blend_colors(const vector rgb1, rgb2; const int method)
{
    if (method == COLOR_BLEND_NORMAL)
        return rgb2;

    if (method == COLOR_BLEND_DARKEN)
        return min(rgb1, rgb2);
    if (method == COLOR_BLEND_MULTIPLY)
        return rgb1 * rgb2;
    if (method == COLOR_BLEND_COLOR_BURN)
        return 1 - (1 - rgb1) / rgb2;
    if (method == COLOR_BLEND_LINEAR_BURN)
        return rgb1 + rgb2 - 1;
    if (method == COLOR_BLEND_DARKER_COLOR)
    {
        float lum1 = rel_luminance(rgb1);
        float lum2 = rel_luminance(rgb2);
        return (lum1 > lum2) * rgb2 + (lum1 <= lum2) * rgb1;
    }

    if (method == COLOR_BLEND_LIGHTEN)
        return max(rgb1, rgb2);
    if (method == COLOR_BLEND_SCREEN)
        return 1 - (1 - rgb1) * (1 - rgb2);
    if (method == COLOR_BLEND_COLOR_DODGE)
        return rgb1 / (1 - rgb2);
    if (method == COLOR_BLEND_LINEAR_DODGE)
        return rgb1 + rgb2;
    if (method == COLOR_BLEND_LIGHTER_COLOR)
    {
        float lum1 = rel_luminance(rgb1);
        float lum2 = rel_luminance(rgb2);
        return (lum1 > lum2) * rgb1 + (lum1 <= lum2) * rgb2;
    }

    if (method == COLOR_BLEND_OVERLAY)
        return (avg(rgb1) > 0.5) * (1 - 2 * (1 - rgb1) * (1 - rgb2)) +
               (avg(rgb1) <= 0.5) * (rgb1 * rgb2 * 2);
    if (method == COLOR_BLEND_SOFT_LIGHT)
        return (avg(rgb2) > 0.5) * (1 - (1 - rgb1) * (1 - (rgb2 - 0.5))) +
               (avg(rgb2) <= 0.5) * (rgb1 * (rgb2 + 0.5));
    if (method == COLOR_BLEND_HARD_LIGHT)
        return (avg(rgb2) > 0.5) * (1 - (1 - rgb1) * (1 - 2 * (rgb2 - 0.5))) +
               (avg(rgb2) <= 0.5) * (rgb1 * (2 * rgb2));

    if (method == COLOR_BLEND_DIFFERENCE)
        return abs(rgb1 - rgb2);
    if (method == COLOR_BLEND_EXCLUDE)
        return rgb1 + rgb2 - 2 * rgb1 * rgb2;
    if (method == COLOR_BLEND_SUBTRACT)
        return rgb1 - rgb2;
    if (method == COLOR_BLEND_DIVIDE)
        return rgb1 / rgb2;

    if (method == COLOR_BLEND_HUE)
    {
        vector hsl1 = rgb_to_hsl(rgb1);
        vector hsl2 = rgb_to_hsl(rgb2);
        return hsl_to_rgb(hsl2.x, hsl1.y, hsl1.z);
    }
    if (method == COLOR_BLEND_SATURATION)
    {
        vector hsl1 = rgb_to_hsl(rgb1);
        vector hsl2 = rgb_to_hsl(rgb2);
        return hsl_to_rgb(hsl1.x, hsl2.y, hsl1.z);
    }
    if (method == COLOR_BLEND_COLOR)
    {
        vector hsl1 = rgb_to_hsl(rgb1);
        vector hsl2 = rgb_to_hsl(rgb2);
        return hsl_to_rgb(hsl2.x, hsl2.y, hsl1.z);
    }
    if (method == COLOR_BLEND_LUMINOSITY)
    {
        vector hsl1 = rgb_to_hsl(rgb1);
        vector hsl2 = rgb_to_hsl(rgb2);
        return hsl_to_rgb(hsl1.x, hsl1.y, hsl2.z);
    }

    return rgb2;
}

vector
blend_colors(const vector rgb1, rgb2; const string method_name)
{
    int method = find({'normal',
                       'darken',
                       'multiply',
                       'color_burn',
                       'linear_burn',
                       'darker_color',
                       'lighten',
                       'screen',
                       'color_dodge',
                       'linear_dodge',
                       'lighter_color',
                       'overlay',
                       'soft_light',
                       'hard_light',
                       'difference',
                       'exclusion',
                       'subtract',
                       'divide',
                       'hue',
                       'saturation',
                       'color',
                       'luminosity'}, method_name);
    return blend_colors(rgb1, rgb2, method);
}

// https://en.wikipedia.org/wiki/Color_difference#CIE94

float
delta_e94(const vector lab1, lab2; const float KL, K1, K2)
{
    float KC = 1;
    float KH = 1;

    float delta_a = lab1.y - lab2.y;
    float delta_b = lab1.z - lab2.z;

    float C1 = sqrt((lab1.y * lab1.y) + (lab1.z * lab1.z));
    float C2 = sqrt((lab2.y * lab1.y) + (lab2.z * lab1.z));

    float delta_L = lab1.x - lab2.x;
    float delta_C = C1 - C2;
    float delta_H2 = (delta_a * delta_a) + (delta_b * delta_b) - (delta_C * delta_C);

    float SL = 1;
    float SC = 1 + K1 * C1;
    float SH = 1 + K2 * C1;

    float L = (delta_L / (KL * SL)) * (delta_L / (KL * SL));
    float C = (delta_C / (KC * SC)) * (delta_C / (KC * SC));
    float H = delta_H2 / ((KH * SH) * (KH * SH));
    return sqrt(L + C + H);
}

float
delta_e94(const vector lab1, lab2; const vector weights)
{
    return delta_e94(lab1, lab2, weights.x, weights.y, weights.z);
}

float
delta_e94(const vector lab1, lab2)
{
    float kL = 1;
    float K1 = 0.045;
    float K2 = 0.015;

    return delta_e94(lab1, lab2, kL, K1, K2);
}

// https://en.wikipedia.org/wiki/Color_difference#CIEDE2000

float
delta_e2000(const vector lab1, lab2)
{
    error('Not Implemented');
}


#endif  // _COLORUTILS_H_
