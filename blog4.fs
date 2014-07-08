#version 330
// Pixel color passed to the fragment shaders (RGBA).
in vec3 col;
out vec4 out_color;
 
void main()
{
    out_color = vec4(col, 1);
}
