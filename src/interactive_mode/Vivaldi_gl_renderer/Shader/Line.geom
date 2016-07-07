#version 410
uniform mat4 ModelViewMatrix;
uniform mat4 ProjectionMatrix;
uniform float radius;

layout(lines) in;
layout (line_strip, max_vertices = 102) out;
in vec4 Color[2];
out vec4 VertexColor;

void main(void)
{
	vec4 p1 = vec4(gl_in[0].gl_Position.xyz, 1.0);
	vec4 p2 = vec4(gl_in[1].gl_Position.xyz, 1.0);
	if(gl_in[1].gl_Position.w < 0)
	{
		gl_Position = ProjectionMatrix * ModelViewMatrix * p1;
		VertexColor = Color[0];
		EmitVertex();
		gl_Position = ProjectionMatrix * ModelViewMatrix * p2;
		VertexColor = Color[1];
		EmitVertex();

		EndPrimitive();
	}
}