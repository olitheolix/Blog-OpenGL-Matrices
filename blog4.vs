#version 330 core
// Vertex position.
layout(location = 0) in vec3 vert_col;
layout(location = 1) in vec4 v_N;

out vec3 col;

void main()
{
    gl_Position = v_N;
    col = vert_col;
}
