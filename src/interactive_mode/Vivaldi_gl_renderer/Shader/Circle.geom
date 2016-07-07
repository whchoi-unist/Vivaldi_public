#version 410
		
uniform mat4 ModelViewMatrix;
uniform mat4 ProjectionMatrix;
uniform float radius;
layout(points) in;
layout (triangle_strip, max_vertices = 93) out;
in vec4 Color[1];
out vec4 vPosition;
out vec3 aNormal;
out vec4 VertexColor;

const float PI = 3.1415926;

void genCircle(vec4 p1){
	
   	int i;
   	int m = 15;
   	float theta;
	vec3 q, perp;
	vec3 v1, v2;
	vec4 pos = p1;
	vec4 camPos = (inverse(ModelViewMatrix)) * vec4(0,0,-100000, 1);
	vec3 normalVector = pos.xyz - camPos.xyz;

	perp = normalVector;
	if (normalVector.x == 0 && normalVector.z == 0)
		perp.z += 1;
	else
		perp.y += 1;

	q = cross(perp, normalVector);
	perp = cross(normalVector, q);
	perp = normalize(perp);
	q = normalize(q);

	for (i=0;i<=m;i+=1) {

		gl_Position = ProjectionMatrix * ModelViewMatrix * (pos - 0.5*radius*normalize(camPos));
		vPosition = ProjectionMatrix * ModelViewMatrix * (pos + radius*normalize(camPos));
		VertexColor = Color[0];
		aNormal = normalize(camPos).xyz;
		EmitVertex();

		theta = (i+1) * ((2 * PI) / m );
		normalVector.x = cos(theta) * perp.x + sin(theta) * q.x;
		normalVector.y = cos(theta) * perp.y + sin(theta) * q.y;
		normalVector.z = cos(theta) * perp.z + sin(theta) * q.z;
		normalVector = normalize(normalVector);

		v2.x = pos.x + radius * normalVector.x;
		v2.y = pos.y + radius * normalVector.y;
		v2.z = pos.z + radius * normalVector.z;


		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v2,1.0);
		vPosition = ProjectionMatrix * ModelViewMatrix * (pos + radius*normalize(camPos));
		VertexColor = Color[0];
		aNormal = normalVector;
		EmitVertex();


		theta = i * ((2 * PI) / m );
		normalVector.x = cos(theta) * perp.x + sin(theta) * q.x;
		normalVector.y = cos(theta) * perp.y + sin(theta) * q.y;
		normalVector.z = cos(theta) * perp.z + sin(theta) * q.z;
		normalVector = normalize(normalVector);

		v1.x = pos.x + radius * normalVector.x;
		v1.y = pos.y + radius * normalVector.y;
		v1.z = pos.z + radius * normalVector.z;

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v1,1.0);
		vPosition = ProjectionMatrix * ModelViewMatrix * (pos + radius*normalize(camPos));
		VertexColor = Color[0];
		aNormal = normalVector;
		EmitVertex();		


		EndPrimitive();

	}
}

void main(void)
{
	genCircle(gl_in[0].gl_Position);
}