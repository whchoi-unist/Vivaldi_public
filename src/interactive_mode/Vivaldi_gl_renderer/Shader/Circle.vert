in vec4 VertexPosition;
varying out vec4 Color;
void main()
{
	gl_Position = vec4(VertexPosition.xyz, 1.0);
	Color = gl_Color;
}