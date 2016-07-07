in vec4 VertexPosition;
varying out vec4 Color;
void main()
{
	gl_Position = VertexPosition;
	Color = gl_Color;
}