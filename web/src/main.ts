import "./styles.css";
import data from "virtual:arshia";
import { mount } from "./render";
import { motion } from "./motion";
import { form } from "./form";

mount(data);
form(data);
motion();
