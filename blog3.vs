#version 330 core
// Vertex position.
layout(location = 0) in vec4 v_N;

void main()
{
    gl_Position = v_N;
}
