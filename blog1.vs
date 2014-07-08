#version 330 core
// Vertex position.
layout(location = 0) in vec3 v_N;

void main()
{
    gl_Position = vec4(v_N, 1);
}
