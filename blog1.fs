#version 330
// Pixel color passed to the fragment shaders (RGBA).
out vec4 out_color;
 
void main()
{
    // Every triangle fragment is yellow (R=1, G=1, B=0) and
    // fully non-transparent (A=1).
    out_color = vec4(1, 1, 0, 1);
}
