const Joi = require("joi");

const express = require("express"); // will create a function

const app = express(); // creating an object

app.use(express.json()); //enabling posting JSON objects, which is not native

const courses = [
	{id: 1, name: "course1"},
	{id: 2, name: "course2"},
	{id: 3, name: "course3"}
];
	
// app.get(), app.post(), app.put(), app.delete()

app.get("/", (req, res) => {
	res.send("Hello world!!!");
});

app.get("/api/courses", (req, res) => {
	res.send(courses);
});

app.post("/api/courses", (req, res) => {

	const {error} = validateCourse(req.body); // result.error ... object destructuring 
	if(error) return res.status(400).send(error.details[0].message);
		//400 Bad Request

	const course = {
		id: courses.length + 1,
		name: req.body.name
	};

	courses.push(course);
	res.send(course); //because user wants to know the ID
});

app.put("/api/courses/:id", (req, res) => {
	// Look up the course
	// If not existing, return 404
	const course = courses.find(c => c.id === parseInt(req.params.id));
	if (!course) return res.status(404).send("The course with the given ID was not found");

	// Validate
	// If invalid, return 400 - Bad request
	const {error} = validateCourse(req.body); // result.error ... object destructuring 
	if(error) {
		res.status(400).send(error.details[0].message);
		return; // we dont want the rest of function to be executed
	}

	// Update course
	course.name = req.body.name;
	// Return the updated course
	res.send(course);
});

app.delete("/api/courses/:id", (req, res) => {
    // Look up the course
    // Non existing, return 404
    const course = courses.find(c => c.id === parseInt(req.params.id));
	if (!course) return res.status(404).send("The course with the given ID was not found");

    // Delete
    const index = courses.indexOf(course);
    courses.splice(index, 1);

    // Return the same course
    res.send(course);
});

app.get("/api/courses/:id", (req, res) => {
	const course = courses.find(c => c.id === parseInt(req.params.id));
	if (!course) return res.status(404).send("The course with the given ID was not found");
	res.send(course);
});

// PORT
const port = process.env.PORT || 3000; // environment variable or 3000 if undefined
app.listen(port, () => console.log(`Listening on port ${port}...`));

function validateCourse(course) {
	const schema = {
		name: Joi.string().min(3).required()
	};
	return Joi.validate(course, schema); //returns an object
}

