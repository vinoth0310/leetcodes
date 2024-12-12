package test;

public class StringManipulation {
    public void addSplChar(String str) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < str.length(); i++) {
            sb.append(str.charAt(i));
            if (i < str.length() - 1) {
                sb.append("#");
            }
        }
//        System.out.println(sb.toString());
        System.out.println("#" + str.replaceAll("(.)","$1#"));
        System.out.println(str.replaceAll("","#"));
    }

    public static void main(String[] args) {

        StringManipulation sm = new StringManipulation();
        sm.addSplChar("sample");
    }
}
