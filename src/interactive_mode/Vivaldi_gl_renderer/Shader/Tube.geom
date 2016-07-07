#version 410
uniform mat4 ModelViewMatrix;
uniform mat4 ProjectionMatrix;
uniform float radius;

layout(lines) in;
layout (triangle_strip, max_vertices = 102) out;
in vec4 Color[2];
out vec4 VertexColor;
out vec3 aNormal;
const float PI = 3.1415926;

void genTube(vec4 p1, vec4 p2){
	
   	int i;
   	int m = 12;
   	float theta;
		
	vec3 q, perp;
	vec3 v1, v2, v3, v4;
	vec3 n12, n34;
	vec3 normalVector = p1.xyz - p2.xyz;

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
		theta = i * ((2 * PI) / m );
		normalVector.x = cos(theta) * perp.x + sin(theta) * q.x;
		normalVector.y = cos(theta) * perp.y + sin(theta) * q.y;
		normalVector.z = cos(theta) * perp.z + sin(theta) * q.z;
		normalVector = normalize(normalVector);

		v1.x = p2.x + radius * normalVector.x;
		v1.y = p2.y + radius * normalVector.y;
		v1.z = p2.z + radius * normalVector.z;

		v2.x = p1.x + radius * normalVector.x;
		v2.y = p1.y + radius * normalVector.y;
		v2.z = p1.z + radius * normalVector.z;

		n12 = normalVector;

		theta = (i+1) * ((2 * PI) / m );
		normalVector.x = cos(theta) * perp.x + sin(theta) * q.x;
		normalVector.y = cos(theta) * perp.y + sin(theta) * q.y;
		normalVector.z = cos(theta) * perp.z + sin(theta) * q.z;
		normalVector = normalize(normalVector);

		v3.x = p2.x + radius * normalVector.x;
		v3.y = p2.y + radius * normalVector.y;
		v3.z = p2.z + radius * normalVector.z;
		
		v4.x = p1.x + radius * normalVector.x;
		v4.y = p1.y + radius * normalVector.y;
		v4.z = p1.z + radius * normalVector.z;				

		n34 = normalVector;

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v1,1.0);
		aNormal = n12;
		VertexColor = Color[0];
		EmitVertex();		

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v2,1.0);
		aNormal = n12;
		VertexColor = Color[1];
		EmitVertex();
			
		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v3,1.0);
		aNormal = n34;
		VertexColor = Color[0];
		EmitVertex();
		EndPrimitive();

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v2,1.0);
		aNormal = n12;
		VertexColor = Color[1];
		EmitVertex();

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v4,1.0);
		aNormal = n34;
		VertexColor = Color[1];
		EmitVertex();

		gl_Position = ProjectionMatrix * ModelViewMatrix * vec4(v3,1.0);
		aNormal = n34;
		VertexColor = Color[0];
		EmitVertex();
		EndPrimitive();
		}
}

void main(void)
{
	vec4 p1 = vec4(gl_in[0].gl_Position.xyz, 1.0);
	vec4 p2 = vec4(gl_in[1].gl_Position.xyz, 1.0);
	if(gl_in[1].gl_Position.w < 0)
		genTube(p1, p2);
}